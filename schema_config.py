
DATASET_META = {
    'secure_dataset': {
        'id': 'secure_dataset',
        'label_ko': '코어 앱 DB',
        'source_system': 'Main App (AWS RDS)',
        'sync_frequency': 'real-time',
        'color': '#3b82f6',
        'tier': 1
    },
    'product': {
        'id': 'product',
        'label_ko': '스팟 예약',
        'source_system': 'Supabase sync',
        'sync_frequency': 'daily 01:00 KST',
        'color': '#22c55e',
        'tier': 1
    },
    'spot': {
        'id': 'spot',
        'label_ko': '커버링스팟 운영',
        'source_system': 'Supabase sync',
        'sync_frequency': 'daily 01:00 KST',
        'color': '#10b981',
        'tier': 1
    },
    'mixpanel': {
        'id': 'mixpanel',
        'label_ko': 'Mixpanel 이벤트',
        'source_system': 'Mixpanel native connector',
        'sync_frequency': 'real-time',
        'color': '#a855f7',
        'tier': 1
    },
    'airbridge_dataset': {
        'id': 'airbridge_dataset',
        'label_ko': 'Airbridge 광고',
        'source_system': 'Google Apps Script',
        'sync_frequency': 'daily',
        'color': '#f97316',
        'tier': 2
    },
    'cx_data': {
        'id': 'cx_data',
        'label_ko': 'CX 상담',
        'source_system': 'Channel Talk + Apps Script',
        'sync_frequency': 'trigger',
        'color': '#ec4899',
        'tier': 2
    },
    'bag_delivery': {
        'id': 'bag_delivery',
        'label_ko': '봉투 배송',
        'source_system': 'Google Sheets manual',
        'sync_frequency': 'manual',
        'color': '#eab308',
        'tier': 2
    },
    'ads_data': {
        'id': 'ads_data',
        'label_ko': '광고 비용',
        'source_system': 'Airbridge + Apps Script',
        'sync_frequency': 'daily',
        'color': '#f59e0b',
        'tier': 2
    },
}

EDGES = [
    {'source': 'secure_dataset.user', 'target': 'secure_dataset.order', 'source_col': 'id', 'target_col': 'user_id', 'rel': '1:N'},
    {'source': 'secure_dataset.order', 'target': 'secure_dataset.order_receipt_v2', 'source_col': 'id', 'target_col': 'order_id', 'rel': '1:1'},
    {'source': 'secure_dataset.order', 'target': 'secure_dataset.order_status_log', 'source_col': 'id', 'target_col': 'order_id', 'rel': '1:N'},
    {'source': 'secure_dataset.order', 'target': 'secure_dataset.order_image', 'source_col': 'id', 'target_col': 'order_id', 'rel': '1:N'},
    {'source': 'secure_dataset.user', 'target': 'secure_dataset.user_address', 'source_col': 'id', 'target_col': 'user_id', 'rel': '1:N'},
    {'source': 'secure_dataset.user_address', 'target': 'secure_dataset.address', 'source_col': 'address_id', 'target_col': 'id', 'rel': 'N:1'},
    {'source': 'secure_dataset.address', 'target': 'secure_dataset.service_region', 'source_col': 'h_code', 'target_col': 'h_code', 'rel': 'N:1'},
    {'source': 'secure_dataset.order', 'target': 'secure_dataset.address', 'source_col': 'address_id', 'target_col': 'id', 'rel': 'N:1'},
    {'source': 'secure_dataset.user', 'target': 'secure_dataset.subscription', 'source_col': 'id', 'target_col': 'user_id', 'rel': '1:N'},
    {'source': 'secure_dataset.subscription', 'target': 'secure_dataset.subscription_plan', 'source_col': 'subscription_plan_id', 'target_col': 'id', 'rel': 'N:1'},
    {'source': 'secure_dataset.subscription', 'target': 'secure_dataset.subscription_invoice', 'source_col': 'id', 'target_col': 'subscription_id', 'rel': '1:N'},
    {'source': 'secure_dataset.subscription_invoice', 'target': 'secure_dataset.payment_event', 'source_col': 'invoice_id', 'target_col': 'invoice_id', 'rel': '1:N'},
    {'source': 'secure_dataset.user', 'target': 'secure_dataset.assignment', 'source_col': 'id', 'target_col': 'user_id', 'rel': '1:N'},
    {'source': 'secure_dataset.assignment', 'target': 'secure_dataset.experiment', 'source_col': 'experiment_id', 'target_col': 'id', 'rel': 'N:1'},
    {'source': 'secure_dataset.order', 'target': 'secure_dataset.coupon', 'source_col': 'user_coupon_id', 'target_col': 'id', 'rel': 'N:1'},
    {'source': 'secure_dataset.coupon', 'target': 'secure_dataset.coupon_policy', 'source_col': 'coupon_policy_id', 'target_col': 'id', 'rel': 'N:1'},
    {'source': 'secure_dataset.order', 'target': 'secure_dataset.payment_policy', 'source_col': 'payment_policy_id', 'target_col': 'id', 'rel': 'N:1'},
    {'source': 'secure_dataset.service_region', 'target': 'secure_dataset.payment_policy', 'source_col': 'payment_policy_id', 'target_col': 'id', 'rel': 'N:1'},
    {'source': 'secure_dataset.user', 'target': 'secure_dataset.device', 'source_col': 'id', 'target_col': 'user_id', 'rel': '1:N'},
    {'source': 'secure_dataset.user', 'target': 'mixpanel.mp_master_event', 'source_col': 'id', 'target_col': 'user_id', 'rel': '1:N', 'note': 'CAST(user.id AS STRING)'},
    {'source': 'secure_dataset.user', 'target': 'product.spot_user_matching', 'source_col': 'id', 'target_col': 'covering_user_id', 'rel': '1:N'},
    {'source': 'spot.bookings', 'target': 'spot.drivers', 'source_col': 'driver_id', 'target_col': 'id', 'rel': 'N:1'},
]

EXTERNAL_SYSTEMS = {
    'ext_main_app': {'id': 'ext_main_app', 'name': 'Main App (AWS)', 'tier': 1, 'sync_frequency': 'real-time', 'sync_method': 'CDC', 'direction': 'inbound', 'connected_datasets': ['secure_dataset']},
    'ext_mixpanel': {'id': 'ext_mixpanel', 'name': 'Mixpanel', 'tier': 1, 'sync_frequency': 'real-time', 'sync_method': 'Native BQ Connector', 'direction': 'inbound', 'connected_datasets': ['mixpanel']},
    'ext_supabase': {'id': 'ext_supabase', 'name': 'Supabase (covering-spot)', 'tier': 1, 'sync_frequency': 'daily', 'sync_method': 'GitHub Actions BQ Sync', 'direction': 'inbound', 'connected_datasets': ['product', 'spot']},
    'ext_airbridge': {'id': 'ext_airbridge', 'name': 'Airbridge', 'tier': 2, 'sync_frequency': 'daily', 'sync_method': 'Apps Script', 'direction': 'inbound', 'connected_datasets': ['airbridge_dataset', 'ads_data']},
    'ext_channel_talk': {'id': 'ext_channel_talk', 'name': 'Channel Talk', 'tier': 2, 'sync_frequency': 'trigger', 'sync_method': 'Apps Script', 'direction': 'inbound', 'connected_datasets': ['cx_data']},
    'ext_google_sheets': {'id': 'ext_google_sheets', 'name': 'Google Sheets', 'tier': 2, 'sync_frequency': 'manual', 'sync_method': 'Manual Upload', 'direction': 'inbound', 'connected_datasets': ['bag_delivery']},
    'ext_flareline': {'id': 'ext_flareline', 'name': 'Flareline (CRM)', 'tier': 3, 'sync_frequency': 'event-driven', 'sync_method': 'Webhook', 'direction': 'outbound', 'connected_datasets': []},
    'ext_slack': {'id': 'ext_slack', 'name': 'Slack', 'tier': 3, 'sync_frequency': 'event-driven', 'sync_method': 'Webhook/launchd', 'direction': 'outbound', 'connected_datasets': []},
    'ext_notion': {'id': 'ext_notion', 'name': 'Notion', 'tier': 3, 'sync_frequency': 'manual/cron', 'sync_method': 'API', 'direction': 'both', 'connected_datasets': []},
    'ext_solapi': {'id': 'ext_solapi', 'name': 'Solapi (SMS)', 'tier': 3, 'sync_frequency': 'event-driven', 'sync_method': 'API', 'direction': 'outbound', 'connected_datasets': []},
}

TABLE_OVERRIDES = {
    'secure_dataset.user': {
        'pk': ['id'], 'label_ko': '사용자', 'description': '서비스 이용 고객',
        'enums': {
            'signup_referral_channel': ['ADS', 'FRIEND_REFERRAL', 'ETC', 'APPSTORE_GOOGLEPLAY', 'BLOG', 'INFLUENCER', 'NEIGHBOR_USE', 'COVERING_CAR', 'CAFE'],
            'grade': ['NORMAL', 'VIP', 'VVIP']
        }
    },
    'secure_dataset.order': {
        'pk': ['id'], 'label_ko': '주문', 'description': '정기수거 주문',
        'enums': {
            'status': ['PAYMENT_COMPLETED', 'COMPLETED', 'CHECK_COMPLETED', 'USER_CANCELED', 'ADMIN_CANCELED', 'SUBMIT', 'READY', 'RUNNING'],
            'request_type': ['DEFAULT_GARBAGE', 'RECYCLING'],
            'customer_type': ['INDIVIDUAL', 'BUSINESS']
        }
    },
    'secure_dataset.order_receipt_v2': {
        'pk': ['order_id'], 'label_ko': '주문 영수증', 'description': '결제 영수증',
        'enums': {
            'payment_status': ['COMPLETED', 'PENDING', 'REFUNDED', 'PARTIALLY_REFUNDED'],
            'payment_method_type': ['CARD', 'TRANSFER', 'VIRTUAL_ACCOUNT']
        }
    },
    'secure_dataset.order_status_log': {'pk': [], 'label_ko': '주문 상태 로그', 'description': '주문 상태 변경 이력'},
    'secure_dataset.order_image': {'pk': [], 'label_ko': '주문 사진', 'description': '수거 전후 사진'},
    'secure_dataset.user_address': {'pk': [], 'label_ko': '사용자 주소', 'description': '사용자의 등록 주소 (active=true가 현재 주소)'},
    'secure_dataset.address': {'pk': ['id'], 'label_ko': '주소', 'description': '실제 주소 정보 + h_code(법정동코드)'},
    'secure_dataset.service_region': {'pk': ['h_code'], 'label_ko': '서비스 지역', 'description': '수거 가능 지역 및 요일/요금 정책'},
    'secure_dataset.subscription': {
        'pk': ['id'], 'label_ko': '구독', 'description': '정기결제 구독 현황',
        'enums': {'status': ['ACTIVE', 'CANCELED', 'PENDING']}
    },
    'secure_dataset.subscription_plan': {'pk': ['id'], 'label_ko': '구독 플랜', 'description': '구독 상품 (가격/주기)'},
    'secure_dataset.subscription_invoice': {'pk': ['id'], 'label_ko': '구독 청구서', 'description': '정기결제 청구 이력'},
    'secure_dataset.invoice': {'pk': ['id'], 'label_ko': '청구서 (레거시)', 'description': '레거시 청구서'},
    'secure_dataset.payment_event': {
        'pk': [], 'label_ko': '결제 이벤트', 'description': '실제 결제 발생 이벤트',
        'enums': {'status': ['COMPLETED', 'FAILED', 'PENDING']}
    },
    'secure_dataset.payment_policy': {'pk': ['id'], 'label_ko': '요금 정책', 'description': '지역별 수거 요금'},
    'secure_dataset.assignment': {'pk': [], 'label_ko': '실험 배정', 'description': 'A/B 테스트 사용자 배정'},
    'secure_dataset.experiment': {
        'pk': ['id'], 'label_ko': '실험', 'description': 'A/B 테스트 메타데이터',
        'enums': {'status': ['RUNNING', 'COMPLETED', 'PAUSED']}
    },
    'secure_dataset.coupon': {'pk': ['id'], 'label_ko': '쿠폰', 'description': '사용자에게 발급된 쿠폰'},
    'secure_dataset.coupon_policy': {
        'pk': ['id'], 'label_ko': '쿠폰 정책', 'description': '쿠폰 할인 규칙',
        'enums': {'discount_type': ['FIXED', 'PERCENTAGE']}
    },
    'secure_dataset.device': {'pk': [], 'label_ko': '디바이스', 'description': '사용자 기기 정보 및 마케팅 수신 동의'},
    'product.bookings': {
        'pk': ['booking_id'], 'label_ko': '방문수거 예약', 'description': '대형폐기물 방문수거 예약 (covering-spot)',
        'enums': {
            'status': ['CONFIRMED', 'CANCELED', 'COMPLETED'],
            'payment_status': ['settled', 'unsettled']
        }
    },
    'product.spot_user_matching': {'pk': [], 'label_ko': '스팟-메인앱 연결', 'description': '방문수거 고객을 메인앱 사용자와 연결'},
    'spot.bookings': {'pk': ['id'], 'label_ko': '스팟 배차', 'description': '방문수거 배차 상세 정보'},
    'spot.drivers': {'pk': ['id'], 'label_ko': '기사', 'description': '방문수거 기사 정보'},
    'spot.leads': {'pk': ['id'], 'label_ko': '견적 요청', 'description': '미확정 방문수거 견적 요청'},
    'spot.spot_items': {'pk': ['id'], 'label_ko': '수거 품목', 'description': '방문수거 가능 품목 및 단가'},
    'mixpanel.mp_master_event': {'pk': [], 'label_ko': 'Mixpanel 이벤트', 'description': '앱 내 모든 사용자 행동 이벤트 (파티션: _PARTITIONDATE)'},
    'mixpanel.mp_people_data_view': {'pk': [], 'label_ko': 'Mixpanel 사용자 프로필', 'description': 'Mixpanel 사용자 속성 데이터'},
}
