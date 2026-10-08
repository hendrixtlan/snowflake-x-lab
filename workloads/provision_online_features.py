"""Explicitly provision a single-tenant Postgres Online Feature Store experiment.

This will create a continuously billed online service. It never runs in CI.
Requires an administrator to have created separate producer and consumer roles.
"""
from __future__ import annotations

import argparse
import json
import os


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database', default='MUSIC_LAB')
    parser.add_argument('--feature-store', default='XLAB_FS')
    parser.add_argument('--warehouse', default='MUSIC_LAB_XS')
    parser.add_argument('--producer-role', required=True)
    parser.add_argument('--consumer-role', required=True)
    parser.add_argument('--tenant-id', default='t1', choices=['t1'])
    parser.add_argument('--destroy-online-service', action='store_true', help='Stop billing by dropping the online service')
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    if not args.apply or os.environ.get('XLAB_ACK_COST') != 'YES':
        print(json.dumps({'status': 'dry_run', 'action': 'destroy' if args.destroy_online_service else 'provision',
                          'warning': 'Explicit --apply plus XLAB_ACK_COST=YES required; service incurs continuous charges.'}))
        return

    from snowflake.snowpark import Session
    from snowflake.ml.feature_store import (
        FeatureStore, CreationMode, Entity, FeatureView, OnlineConfig, OnlineStoreType
    )
    from snowflake.ml.feature_store.online_service import OnlineServiceAccess

    session = Session.builder.config('connection_name', os.environ.get('SNOWFLAKE_CONNECTION_NAME', 'xlab')).create()
    fs = None
    try:
        fs = FeatureStore(session=session, database=args.database, name=args.feature_store,
                          default_warehouse=args.warehouse, creation_mode=CreationMode.CREATE_IF_NOT_EXIST,
                          online_service_access=OnlineServiceAccess.PUBLIC)
        if args.destroy_online_service:
            fs.drop_online_service()
            print(json.dumps({'status': 'drop_online_service_requested', 'feature_store': args.feature_store}))
            return
        # Do not combine multiple tenants in this consumer's shared feature view.
        entity = fs.register_entity(Entity('T1_LISTENER', ['USER_ID'], desc='Synthetic t1 listener only'))
        source_df = session.table(f'{args.database}.FEATURES.DT_USER_COUNTS').filter("TENANT_ID = 't1'")
        feature_view = FeatureView(
            name='T1_USER_ENGAGEMENT',
            entities=[entity],
            feature_df=source_df,
            timestamp_col='LATEST_EVENT_TS',
            refresh_freq='1 minute',
            online_config=OnlineConfig(enable=True, target_lag='10s', store_type=OnlineStoreType.POSTGRES),
            desc='t1 only: materialized user engagement. NOT sub-2s streaming freshness.'
        )
        fs.create_online_service(args.producer_role, args.consumer_role)
        fs.register_feature_view(feature_view, version='V1')
        print(json.dumps({'status': 'registered', 'feature_view': 'T1_USER_ENGAGEMENT',
                          'version': 'V1', 'online_service_billable': True,
                          'expected_lag': 'offline refresh (1m) plus online sync (10s), not real-time ingest'}))
    finally:
        if fs is not None and hasattr(fs, 'close'):
            fs.close()
        session.close()


if __name__ == '__main__':
    main()
