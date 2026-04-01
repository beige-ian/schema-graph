
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
    {'source': 'secure_dataset.user', 'target': 'secure_dataset.order_v2', 'source_col': 'id', 'target_col': 'user_id', 'rel': '1:N'},
    {'source': 'secure_dataset.company', 'target': 'secure_dataset.order_v2', 'source_col': 'id', 'target_col': 'company_id', 'rel': '1:N'},
    {'source': 'secure_dataset.order_v2', 'target': 'secure_dataset.user_coupon', 'source_col': 'user_coupon_id', 'target_col': 'id', 'rel': 'N:1'},
    {'source': 'secure_dataset.order_v2', 'target': 'secure_dataset.payment_policy', 'source_col': 'payment_policy_id', 'target_col': 'id', 'rel': 'N:1'},
    {'source': 'secure_dataset.order_v2', 'target': 'secure_dataset.order_customer_snapshot', 'source_col': 'id', 'target_col': 'order_id', 'rel': '1:1'},
    {'source': 'secure_dataset.order_v2', 'target': 'secure_dataset.order_address_snapshot', 'source_col': 'id', 'target_col': 'order_id', 'rel': '1:1'},
    {'source': 'secure_dataset.order_v2', 'target': 'secure_dataset.order_access_instruction', 'source_col': 'id', 'target_col': 'order_id', 'rel': '1:1'},
    {'source': 'secure_dataset.order_v2', 'target': 'secure_dataset.order_line', 'source_col': 'id', 'target_col': 'order_id', 'rel': '1:N'},
    {'source': 'secure_dataset.order_v2', 'target': 'secure_dataset.order_status_event', 'source_col': 'id', 'target_col': 'order_id', 'rel': '1:N'},
    {'source': 'secure_dataset.order_v2', 'target': 'secure_dataset.order_invoice', 'source_col': 'id', 'target_col': 'order_id', 'rel': '1:N'},
    {'source': 'secure_dataset.order_v2', 'target': 'secure_dataset.order_image_v2', 'source_col': 'id', 'target_col': 'order_id', 'rel': '1:N'},
    {'source': 'secure_dataset.order_v2', 'target': 'secure_dataset.fulfillment', 'source_col': 'id', 'target_col': 'order_id', 'rel': '1:N'},
    {'source': 'secure_dataset.order_line', 'target': 'secure_dataset.product', 'source_col': 'product_id', 'target_col': 'id', 'rel': 'N:1'},
    {'source': 'secure_dataset.order_line', 'target': 'secure_dataset.order_line_change_event', 'source_col': 'id', 'target_col': 'order_line_id', 'rel': '1:N'},
    {'source': 'secure_dataset.fulfillment', 'target': 'secure_dataset.rider', 'source_col': 'rider_id', 'target_col': 'id', 'rel': 'N:1'},
    {'source': 'secure_dataset.fulfillment', 'target': 'secure_dataset.fulfillment_item', 'source_col': 'id', 'target_col': 'fulfillment_id', 'rel': '1:N'},
    {'source': 'secure_dataset.fulfillment', 'target': 'secure_dataset.fulfillment_status_event', 'source_col': 'id', 'target_col': 'fulfillment_id', 'rel': '1:N'},
    {'source': 'secure_dataset.fulfillment', 'target': 'secure_dataset.fulfillment_assignment', 'source_col': 'id', 'target_col': 'fulfillment_id', 'rel': '1:N'},
    {'source': 'secure_dataset.fulfillment', 'target': 'secure_dataset.fulfillment_message', 'source_col': 'id', 'target_col': 'fulfillment_id', 'rel': '1:N'},
    {'source': 'secure_dataset.fulfillment_item', 'target': 'secure_dataset.order_line', 'source_col': 'order_line_id', 'target_col': 'id', 'rel': 'N:1'},
    {'source': 'secure_dataset.fulfillment_assignment', 'target': 'secure_dataset.rider', 'source_col': 'rider_id', 'target_col': 'id', 'rel': 'N:1'},
    {'source': 'secure_dataset.fulfillment_message', 'target': 'secure_dataset.rider', 'source_col': 'rider_id', 'target_col': 'id', 'rel': 'N:1'},
    {'source': 'secure_dataset.order_image_v2', 'target': 'secure_dataset.fulfillment', 'source_col': 'fulfillment_id', 'target_col': 'id', 'rel': 'N:1'},
    {'source': 'secure_dataset.order_invoice', 'target': 'secure_dataset.invoice', 'source_col': 'invoice_id', 'target_col': 'id', 'rel': 'N:1'},
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
    {'source': 'secure_dataset.order', 'target': 'secure_dataset.user_coupon', 'source_col': 'user_coupon_id', 'target_col': 'id', 'rel': 'N:1'},
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
        'pk': ['id'], 'label_ko': '주문 (레거시)', 'description': '마이그레이션 이전 주문 모델. 신규 주문/방문은 order_v2 + fulfillment 기준',
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
    'secure_dataset.order_status_log': {'pk': [], 'label_ko': '주문 상태 로그 (레거시)', 'description': '마이그레이션 이전 주문 상태 변경 이력'},
    'secure_dataset.order_image': {'pk': [], 'label_ko': '주문 사진 (레거시)', 'description': '마이그레이션 이전 수거 전후 사진'},
    'secure_dataset.order_v2': {
        'pk': ['id'], 'label_ko': '주문 V2',
        'description': '신규 주문 도메인의 계약 단위 주문. 주문 상태는 계약 단계 기준으로 관리됩니다.',
        'enums': {
            'status': ['CREATED', 'READY', 'IN_PROGRESS', 'COMPLETED', 'CANCELED']
        },
        'columns': {
            'order_number': {'description': '사용자/백오피스에 노출되는 주문 번호'},
            'status': {'description': '주문 전체 계약 상태'},
            'payment_policy_id': {'description': '적용된 결제 정책'},
            'user_coupon_id': {'description': '적용된 사용자 쿠폰'},
            'company_id': {'description': 'B2B 주문인 경우 연결된 기업 고객'},
        }
    },
    'secure_dataset.order_customer_snapshot': {
        'pk': ['id'], 'label_ko': '주문 고객 스냅샷',
        'description': '주문 생성 시점의 고객 이름/전화번호 스냅샷. 전화번호는 마스킹되어 저장됩니다.'
    },
    'secure_dataset.order_address_snapshot': {
        'pk': ['id'], 'label_ko': '주문 주소 스냅샷',
        'description': '주문 시점의 수거 주소 스냅샷. 이후 사용자 주소가 바뀌어도 주문 주소는 유지됩니다.'
    },
    'secure_dataset.order_access_instruction': {
        'pk': ['id'], 'label_ko': '출입 정보',
        'description': '해당 주문 수행에 필요한 출입 방법, 비밀번호, 요청사항.'
    },
    'secure_dataset.order_line': {
        'pk': ['id'], 'label_ko': '주문 품목',
        'description': '주문에 포함된 상품 라인. 봉투 구매/수거 박스/수거 봉투 등을 표현합니다.'
    },
    'secure_dataset.order_line_change_event': {
        'pk': ['id'], 'label_ko': '주문 품목 변경 이력',
        'description': '주문 품목 수량 등 필드 변경 이벤트 로그.'
    },
    'secure_dataset.product': {
        'pk': ['id'], 'label_ko': '상품 마스터',
        'description': '신규 주문 도메인에서 사용하는 상품 정의.',
        'enums': {
            'product_code': [
                'COVERING_BAG',
                'LARGE_COVERING_BAG',
                'PICKUP_BOX',
                'PICKUP_COVERING_BAG',
                'PICKUP_LARGE_COVERING_BAG'
            ]
        }
    },
    'secure_dataset.fulfillment': {
        'pk': ['id'], 'label_ko': '방문/수행',
        'description': '기사 방문 작업 단위. 방문 상태는 수행 단계 기준으로 관리되며 재방문 시 여러 건이 연결될 수 있습니다.',
        'enums': {
            'status': ['CREATED', 'READY', 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELED'],
            'failure_reason_code': ['ACCESS_DENIED', 'NOT_FOUND', 'POLICY_VIOLATION']
        },
        'columns': {
            'status': {'description': '방문 작업 상태'},
            'failure_reason_code': {'description': '실패 유형 코드'},
            'failure_reason_message': {'description': '실패 상세 메시지'},
            'scheduled_start_at': {'description': '방문 예정 시작 시각'},
            'scheduled_end_at': {'description': '방문 예정 종료 시각'},
        }
    },
    'secure_dataset.fulfillment_item': {
        'pk': ['id'], 'label_ko': '방문 품목 수행',
        'description': '방문 시점 기준 품목별 실제 수거 결과와 실패 정보를 기록합니다.'
    },
    'secure_dataset.order_status_event': {
        'pk': ['id'], 'label_ko': '주문 상태 이벤트',
        'description': '주문 상태 변경 이력. from_status/to_status, actor, reason, metadata를 저장합니다.'
    },
    'secure_dataset.fulfillment_status_event': {
        'pk': ['id'], 'label_ko': '방문 상태 이벤트',
        'description': '방문 상태 변경 이력. 실패 사유 파생에 쓰이는 메타데이터가 함께 저장됩니다.'
    },
    'secure_dataset.fulfillment_assignment': {
        'pk': ['id'], 'label_ko': '방문 배정',
        'description': '방문 수행을 기사에게 배정한 이력과 경로 최적화 결과.'
    },
    'secure_dataset.fulfillment_message': {
        'pk': ['id'], 'label_ko': '방문 메시지',
        'description': '방문 수행 과정에서 기사에게 발송된 메시지 이력.'
    },
    'secure_dataset.order_invoice': {
        'pk': ['id'], 'label_ko': '주문 청구서 연결',
        'description': '주문과 청구서(invoice)를 연결하는 브리지 테이블.'
    },
    'secure_dataset.order_image_v2': {
        'pk': ['id'], 'label_ko': '주문 이미지 V2',
        'description': '신규 주문 도메인 이미지 저장소. 주문/방문 기준 사진 메타데이터를 기록합니다.'
    },
    'secure_dataset.feature_flag': {
        'pk': ['name'], 'label_ko': '기능 플래그',
        'description': '서비스별 기능 토글 설정.'
    },
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
    # secure_dataset 추가
    'secure_dataset.auth': {'pk': ['id'], 'label_ko': '인증', 'description': '전화번호 인증 코드 발급 및 검증 이력'},
    'secure_dataset.block_user': {'pk': ['id'], 'label_ko': '이용 정지', 'description': '서비스 이용 정지 처리된 사용자 목록'},
    'secure_dataset.comment': {'pk': ['id'], 'label_ko': '주문 코멘트', 'description': '기사·매니저가 주문에 남긴 메모'},
    'secure_dataset.company': {'pk': ['id'], 'label_ko': '기업 고객', 'description': '기업 계약 고객 정보 (B2B)'},
    'secure_dataset.company_address': {'pk': ['id'], 'label_ko': '기업 수거 주소', 'description': '기업 고객의 등록 수거 주소 목록'},
    'secure_dataset.company_schedule': {'pk': ['id'], 'label_ko': '기업 스케줄', 'description': '기업 고객의 정기수거 요일·시간 스케줄'},
    'secure_dataset.display_item': {'pk': ['id'], 'label_ko': '앱 배너', 'description': '앱 내 배너·홍보 컨텐츠 관리'},
    'secure_dataset.manager': {'pk': ['id'], 'label_ko': '어드민 매니저', 'description': '어드민 시스템 접근 권한이 있는 내부 운영자'},
    'secure_dataset.optimize_route_meta': {'pk': ['id'], 'label_ko': '배차 최적화 로그', 'description': '기사 배차 경로 최적화 연산 결과 메타데이터'},
    'secure_dataset.order_receipt': {'pk': ['id'], 'label_ko': '주문 영수증 (레거시)', 'description': '구 결제 영수증 (현재는 order_receipt_v2 사용)'},
    'secure_dataset.prev_db_order': {'pk': ['id'], 'label_ko': '이관 주문', 'description': '구 DB에서 이관된 과거 주문 데이터'},
    'secure_dataset.receipt': {'pk': ['id'], 'label_ko': '영수증 (레거시)', 'description': '구 결제 영수증 (invoice 연계)'},
    'secure_dataset.region_open_subscriber': {'pk': ['id'], 'label_ko': '지역 오픈 알림 신청', 'description': '서비스 미제공 지역에서 오픈 알림 신청한 사용자'},
    'secure_dataset.rider': {'pk': ['id'], 'label_ko': '수거 기사', 'description': '정기수거 담당 기사 계정 및 활성 상태'},
    'secure_dataset.rider_comment_like': {'pk': ['id'], 'label_ko': '코멘트 좋아요', 'description': '기사가 주문 코멘트에 누른 좋아요'},
    'secure_dataset.service_region_group': {'pk': ['id'], 'label_ko': '지역 그룹', 'description': '서비스 지역을 묶어 관리하는 그룹'},
    'secure_dataset.service_region_group_map': {'pk': ['id'], 'label_ko': '지역-그룹 매핑', 'description': '서비스 지역과 지역 그룹 간 N:M 매핑'},
    'secure_dataset.user_coupon': {'pk': ['id'], 'label_ko': '사용자 쿠폰 발급', 'description': '사용자에게 발급된 쿠폰 및 사용 여부'},
    'secure_dataset.user_payment_method': {'pk': ['id'], 'label_ko': '결제 수단', 'description': '사용자가 등록한 카드·결제 수단'},
    'secure_dataset.variant': {'pk': ['id'], 'label_ko': 'A/B 변형 그룹', 'description': 'A/B 테스트의 대조군·실험군 정의'},
    'secure_dataset.withdrawal': {'pk': ['id'], 'label_ko': '탈퇴 이력', 'description': '서비스 탈퇴 사용자의 탈퇴 사유 및 기본 속성'},
    'product.ab_test_cheonan_asan': {'pk': [], 'label_ko': '천안·아산 AB 테스트', 'description': '천안·아산 지역 오픈 AB 테스트 결과'},
    'product.brand_msg_experiment_users': {'pk': [], 'label_ko': '브랜드 메시지 실험 대상', 'description': '브랜드 메시지 AB 테스트 대상 사용자'},
    'product.brand_msg_wave1': {'pk': [], 'label_ko': '브랜드 메시지 1차 발송', 'description': '브랜드 메시지 1차 발송 대상 및 결과'},
    'product.ext_danggeon_pickup': {'pk': [], 'label_ko': '당근 픽업 연동', 'description': '당근마켓 픽업 서비스 연동 데이터'},
    'product.spot_events': {'pk': [], 'label_ko': '스팟 이벤트 (product)', 'description': '스팟 서비스 관련 이벤트 로그 (product 버전)'},
    'product.spot_waste_items': {'pk': [], 'label_ko': '스팟 폐기물 품목', 'description': '스팟 서비스에서 수거한 폐기물 품목 목록'},
    'product.spot_user_matching_backup': {'pk': [], 'label_ko': '스팟 매칭 백업', 'description': '스팟 사용자-수거 매칭 이력 백업본'},
    'spot.spot_areas': {'pk': [], 'label_ko': '스팟 운영 구역', 'description': '스팟 서비스 운영 가능 구역 정의'},
    'spot.spot_events': {'pk': [], 'label_ko': '스팟 이벤트', 'description': '스팟 수거 신청·처리 이벤트 로그'},
    'ads_data.daily_cost': {'pk': [], 'label_ko': '광고 일별 비용', 'description': '채널별 광고 일별 집행 금액'},
    'ads_data.daily_cost_creative': {'pk': [], 'label_ko': '광고 소재별 비용', 'description': '광고 소재(이미지·영상)별 일별 집행 금액'},
    'ads_data.user_acquisition_channel': {'pk': [], 'label_ko': '신규 유저 획득 채널', 'description': '신규 가입 사용자의 유입 광고 채널'},
    'airbridge_dataset.app_events': {'pk': [], 'label_ko': 'Airbridge 앱 이벤트', 'description': '앱 내 사용자 행동 이벤트 (Airbridge MMP 수집)'},
    'airbridge_dataset.tracking_link_events': {'pk': [], 'label_ko': 'Airbridge 트래킹 링크', 'description': '딥링크·공유 링크 클릭 및 전환 이벤트'},
    'airbridge_dataset.web_events': {'pk': [], 'label_ko': 'Airbridge 웹 이벤트', 'description': '웹사이트 방문·전환 이벤트 (Airbridge 수집)'},
    'bag_delivery.bag_stock_input': {'pk': [], 'label_ko': '봉투 입고 이력', 'description': '150L 봉투 창고 입고 수량 및 날짜'},
    'bag_delivery.branch_rider_mapping': {'pk': [], 'label_ko': '지점-기사 배정', 'description': '봉투 배송 지점과 담당 기사 간 매핑'},
    'bag_delivery.ext_walla_requests': {'pk': [], 'label_ko': '왈라 배송 요청', 'description': '외부 배송사(왈라) 봉투 배송 요청 이력'},
    'bag_delivery.walla_matched_users': {'pk': [], 'label_ko': '왈라 매칭 사용자', 'description': '왈라 배송 서비스와 매칭된 사용자 목록'},
    'cx_data.channel_talk': {'pk': [], 'label_ko': '채널톡 대화', 'description': '채널톡 고객 상담 대화 목록'},
    'cx_data.channel_talk_managers': {'pk': [], 'label_ko': '채널톡 상담사', 'description': '채널톡 상담 담당 내부 운영자 목록'},
    'cx_data.channel_talk_messages': {'pk': [], 'label_ko': '채널톡 메시지', 'description': '채널톡 상담 개별 메시지 내용'},
    'cx_data.channel_talk_userchat': {'pk': [], 'label_ko': '채널톡 채팅방', 'description': '채널톡 고객-상담사 채팅방 단위 메타'},
    'cx_data.channel_talk_users': {'pk': [], 'label_ko': '채널톡 사용자', 'description': '채널톡에 등록된 고객 정보'},
    'cx_data.channel_talk_workflow': {'pk': [], 'label_ko': '채널톡 워크플로우', 'description': '채널톡 자동 응대 워크플로우 실행 이력'},
    'mixpanel.mp_identity_mappings_data_20230101_20231231': {'pk': [], 'label_ko': 'Mixpanel ID 매핑 (2023)', 'description': 'Mixpanel 익명 ID와 사용자 ID 매핑 (2023)'},
    'mixpanel.mp_identity_mappings_data_20240101_20241231': {'pk': [], 'label_ko': 'Mixpanel ID 매핑 (2024)', 'description': 'Mixpanel 익명 ID와 사용자 ID 매핑 (2024)'},
    'mixpanel.mp_nessie_export_log': {'pk': [], 'label_ko': 'Mixpanel 내보내기 로그', 'description': 'Mixpanel → BQ 데이터 내보내기 실행 이력'},
    'mixpanel.mp_people_data_20230101_20231231': {'pk': [], 'label_ko': 'Mixpanel 사용자 속성 (2023)', 'description': 'Mixpanel People 사용자 프로필 속성 (2023)'},
    'mixpanel.mp_people_data_20240101_20241231': {'pk': [], 'label_ko': 'Mixpanel 사용자 속성 (2024)', 'description': 'Mixpanel People 사용자 프로필 속성 (2024)'},
    'mixpanel.mp_identity_mappings_data_20250101_20251231': {'pk': [], 'label_ko': 'Mixpanel ID 매핑 (2025)', 'description': 'Mixpanel 익명 ID와 사용자 ID 매핑 (2025)'},
}
