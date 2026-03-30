#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import datetime
import sys
import urllib.request
from google.cloud import bigquery
from google.api_core.exceptions import GoogleAPICallError

# --- 환경 설정 ---
# 이 스크립트는 'schema_config.py' 파일에 정의된 메타데이터를 사용합니다.
# 스크립트와 같은 디렉토리에 아래와 같은 형식의 schema_config.py 파일을 생성해야 합니다.
#
# 예시: schema_config.py
# """
# DATASET_META = {
#     "product": {"name_ko": "상품", "color": "#4285F4"},
#     "secure_dataset": {"name_ko": "보안", "color": "#DB4437"},
#     # ... 다른 데이터셋 정보
# }
#
# TABLE_OVERRIDES = {
#     "product.products": {
#         "name_ko": "상품 마스터",
#         "description": "모든 상품의 기본 정보를 담고 있는 마스터 테이블입니다.",
#         "columns": {
#             "product_id": {"pk": True, "description": "상품 고유 ID"},
#             "seller_id": {"fk": "secure_dataset.sellers.seller_id", "description": "판매자 ID"},
#             "status": {"enum": ["ACTIVE", "SOLD_OUT", "DELETED"], "description": "상품 상태"}
#         }
#     },
#     # ... 다른 테이블 상세 정보
# }
#
# EDGES = [
#     {"source": "product.orders.user_id", "target": "secure_dataset.users.user_id", "description": "주문-사용자 관계"},
#     {"source": "product.reviews.product_id", "target": "product.products.product_id"},
#     {"source": "external.amplitude", "target": "mixpanel.events", "description": "클라이언트 이벤트 전송"},
# ]
#
# EXTERNAL_SYSTEMS = {
#     "amplitude": {"name_ko": "앰플리튜드", "tier": 1, "sync_type": "SDK", "sync_direction": "inbound"},
#     "salesforce": {"name_ko": "세일즈포스", "tier": 2, "sync_type": "API (周期性)", "sync_frequency": "1시간", "sync_direction": "bidirectional"},
#     # ... 다른 외부 시스템 정보
# }
# """
try:
    import schema_config
except ImportError:
    print("오류: schema_config.py 파일을 찾을 수 없습니다. 스크립트와 동일한 디렉토리에 설정 파일을 생성해주세요.", file=sys.stderr)
    sys.exit(1)

# --- 상수 정의 ---
PROJECT_ID = "covering-app-ccd23"
D3_CDN_URL = "https://cdn.jsdelivr.net/npm/d3@7/dist/d3.min.js"
TARGET_DATASETS = [
    'secure_dataset', 'product', 'spot', 'mixpanel', 
    'airbridge_dataset', 'cx_data', 'bag_delivery', 'ads_data'
]

def fetch_bq_schemas() -> dict:
    """지정된 BigQuery 데이터셋들의 스키마를 INFORMATION_SCHEMA에서 조회합니다."""
    print("BigQuery 스키마 조회 시작...")
    client = bigquery.Client(project=PROJECT_ID)
    schemas = {}

    for dataset_id in TARGET_DATASETS:
        query = f"""
            SELECT
                table_name,
                column_name,
                ordinal_position,
                is_nullable,
                data_type
            FROM `{PROJECT_ID}.{dataset_id}.INFORMATION_SCHEMA.COLUMNS`
            ORDER BY table_name, ordinal_position
        """
        try:
            rows = list(client.query(query).result())
            schemas[dataset_id] = {}
            for row in rows:
                table_id = row.table_name
                if table_id not in schemas[dataset_id]:
                    schemas[dataset_id][table_id] = []
                schemas[dataset_id][table_id].append({
                    "name": row.column_name,
                    "type": row.data_type,
                    "nullable": row.is_nullable == 'YES'
                })
            print(f"  {dataset_id}: {len(schemas[dataset_id])}개 테이블")
        except GoogleAPICallError as e:
            print(f"  {dataset_id}: 조회 실패 ({e})", file=sys.stderr)
        except Exception as e:
            print(f"  {dataset_id}: 오류 ({e})", file=sys.stderr)

    print(f"완료: {len(schemas)}개 데이터셋 조회됨.")
    return schemas


def build_graph_data(bq_schemas: dict) -> dict:
    """BigQuery 스키마와 로컬 설정 파일을 병합하여 그래프 데이터를 생성합니다."""
    print("그래프 데이터 빌드 시작...")
    
    tables = []
    table_map = {}
    
    # 1. 테이블 노드 생성
    for dataset_id, tables_in_dataset in bq_schemas.items():
        for table_id, bq_columns in tables_in_dataset.items():
            full_table_id = f"{dataset_id}.{table_id}"
            override = schema_config.TABLE_OVERRIDES.get(full_table_id, {})
            override_cols = override.get("columns", {})
            
            columns = []
            for col in bq_columns:
                col_override = override_cols.get(col['name'], {})
                columns.append({**col, **col_override})

            node_data = {
                "id": full_table_id,
                "type": "table",
                "dataset_id": dataset_id,
                "table_id": table_id,
                "name_ko": override.get("name_ko", table_id),
                "description": override.get("description", ""),
                "columns": columns,
                "column_count": len(columns),
                "dataset_meta": schema_config.DATASET_META.get(dataset_id, {})
            }
            tables.append(node_data)
            table_map[full_table_id] = node_data

    # 2. 외부 시스템 노드 생성
    external_nodes = []
    for system_id, system_info in schema_config.EXTERNAL_SYSTEMS.items():
        node_data = {
            "id": f"external.{system_id}",
            "type": "external",
            "name_ko": system_info.get("name", system_id),
            "tier": system_info.get("tier"),
            "sync_type": system_info.get("sync_method"),
            "sync_frequency": system_info.get("sync_frequency"),
            "sync_direction": system_info.get("direction"),
            "connected_datasets": system_info.get("connected_datasets", []),
        }
        external_nodes.append(node_data)

    # 3. 데이터셋 그룹 앵커 노드 생성
    dataset_nodes = [
        {"id": f"dataset_anchor_{ds_id}", "type": "dataset", "dataset_id": ds_id, **meta}
        for ds_id, meta in schema_config.DATASET_META.items()
    ]
    
    # 4. 엣지 생성
    edges = []
    edge_set = set() # 중복 엣지 방지
    
    # FK 기반 자동 엣지 생성
    for table_node in tables:
        for column in table_node['columns']:
            if 'fk' in column:
                source_id = f"{table_node['id']}.{column['name']}"
                target_id = column['fk']
                
                # full column path에서 table path로 변환
                source_table_id = ".".join(source_id.split(".")[:2])
                target_table_id = ".".join(target_id.split(".")[:2])

                if source_table_id in table_map and target_table_id in table_map:
                    edge_tuple = tuple(sorted((source_table_id, target_table_id)))
                    if edge_tuple not in edge_set:
                        source_dataset = table_map[source_table_id]['dataset_id']
                        target_dataset = table_map[target_table_id]['dataset_id']
                        edge_type = "internal" if source_dataset == target_dataset else "cross-dataset"

                        edges.append({
                            "source": source_table_id,
                            "target": target_table_id,
                            "type": edge_type,
                            "description": f"FK: {column['name']} -> {target_id.split('.')[-1]}"
                        })
                        edge_set.add(edge_tuple)

    # schema_config.py의 EDGES 추가
    for edge in schema_config.EDGES:
        source_id = ".".join(edge['source'].split(".")[:2])
        target_id = ".".join(edge['target'].split(".")[:2])
        edge_tuple = tuple(sorted((source_id, target_id)))

        if edge_tuple not in edge_set:
            source_is_external = source_id.startswith("external.")
            target_is_external = target_id.startswith("external.")

            edge_type = "external"
            if not source_is_external and not target_is_external:
                source_dataset = table_map.get(source_id, {}).get('dataset_id')
                target_dataset = table_map.get(target_id, {}).get('dataset_id')
                if source_dataset and target_dataset:
                    edge_type = "internal" if source_dataset == target_dataset else "cross-dataset"

            desc = edge.get('description', '')
            if not desc and edge.get('source_col') and edge.get('target_col'):
                desc = f"{edge['source_col']} → {edge['target_col']}"
            if edge.get('note'):
                desc += f" ({edge['note']})"

            edges.append({
                "source": source_id,
                "target": target_id,
                "type": edge_type,
                "description": desc,
                "rel": edge.get('rel', ''),
                "source_col": edge.get('source_col', ''),
                "target_col": edge.get('target_col', ''),
            })
            edge_set.add(edge_tuple)

    # _id 컬럼 패턴으로 관계 자동 감지
    all_table_by_name = {}
    for t in tables:
        tname = t['table_id']
        if tname not in all_table_by_name:
            all_table_by_name[tname] = t['id']

    for table_node in tables:
        for column in table_node['columns']:
            col_name = column['name']
            if not col_name.endswith('_id') or col_name == 'id':
                continue
            target_table_name = col_name[:-3]  # _id 제거
            # 같은 데이터셋 우선 매칭
            candidate = f"{table_node['dataset_id']}.{target_table_name}"
            if candidate not in table_map:
                candidate = all_table_by_name.get(target_table_name)
            if not candidate or candidate not in table_map or candidate == table_node['id']:
                continue
            edge_tuple = tuple(sorted((table_node['id'], candidate)))
            if edge_tuple not in edge_set:
                src_ds = table_node['dataset_id']
                tgt_ds = table_map[candidate]['dataset_id']
                edges.append({
                    "source": table_node['id'],
                    "target": candidate,
                    "type": "internal" if src_ds == tgt_ds else "cross-dataset",
                    "description": f"{col_name} → {target_table_name}.id",
                    "rel": "N:1",
                    "source_col": col_name,
                    "target_col": "id",
                })
                edge_set.add(edge_tuple)

    print(f"성공: 테이블 {len(tables)}개, 외부 시스템 {len(external_nodes)}개, 관계 {len(edges)}개 데이터 생성.")
    
    return {
        "tables": tables,
        "external_nodes": external_nodes,
        "dataset_nodes": dataset_nodes,
        "edges": edges,
        "datasets": schema_config.DATASET_META,
        "generated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def generate_html(graph_data: dict) -> str:
    """그래프 데이터를 사용하여 완전한 self-contained HTML 파일을 생성합니다."""
    print("HTML 파일 생성 시작...")
    
    try:
        print(f"D3.js 라이브러리 다운로드 중... ({D3_CDN_URL})")
        req = urllib.request.Request(D3_CDN_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            d3_script_content = response.read().decode('utf-8')
        print("D3.js 라이브러리 다운로드 완료.")
    except Exception as e:
        print(f"오류: D3.js 라이브러리 다운로드 실패. ({e})", file=sys.stderr)
        print("CDN 폴백으로 진행합니다.", file=sys.stderr)
        # 폴백: DOMContentLoaded 이후 CDN에서 로드하여 초기화 순서 보장
        d3_script_content = f'''document.addEventListener("DOMContentLoaded", function() {{
  var s = document.createElement("script");
  s.src = "{D3_CDN_URL}";
  s.onload = function() {{ if (typeof initGraph === "function") initGraph(); }};
  document.head.appendChild(s);
}});'''


    json_data = json.dumps(graph_data, ensure_ascii=False, indent=2)

    html_template = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BigQuery 스키마 관계도</title>
    <style>
        :root {
            --bg-color: #0f0f13;
            --card-color: #1a1a1f;
            --border-color: #2a2a2f;
            --text-color: #d4d4d8;
            --text-muted-color: #888;
            --accent-color: #3b82f6;
            --header-height: 48px;
            --sidepanel-width: 320px;
            --tier1-color: #f59e0b;
            --tier2-color: #84cc16;
            --tier3-color: #6366f1;
        }
        
        @keyframes dash { to { stroke-dashoffset: -100; } }
        
        body {
            margin: 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            display: flex;
            flex-direction: column;
            height: 100vh;
            overflow: hidden;
        }
        header {
            height: var(--header-height);
            flex-shrink: 0;
            background-color: var(--card-color);
            border-bottom: 1px solid var(--border-color);
            display: flex;
            align-items: center;
            padding: 0 16px;
            z-index: 10;
        }
        h1 {
            font-size: 18px;
            margin: 0;
            font-weight: 500;
        }
        .controls {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-left: auto;
        }
        .search-container {
            display: flex;
            align-items: center;
            background-color: var(--bg-color);
            border: 1px solid var(--border-color);
            border-radius: 6px;
        }
        #search-input {
            background: transparent;
            border: none;
            color: var(--text-color);
            padding: 6px 10px;
            outline: none;
            font-size: 14px;
        }
        #search-select {
            background: var(--card-color);
            border: none;
            border-left: 1px solid var(--border-color);
            color: var(--text-color);
            padding: 6px;
            border-radius: 0 5px 5px 0;
            cursor: pointer;
        }
        .filter-group {
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .filter-group .group-label {
            font-size: 12px;
            color: var(--text-muted-color);
            margin-right: 4px;
        }
        .filter-btn {
            padding: 4px 8px;
            font-size: 12px;
            border: 1px solid var(--border-color);
            border-radius: 12px;
            background-color: var(--card-color);
            color: var(--text-muted-color);
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .filter-btn.active {
            color: #fff;
            border-color: var(--color);
            background-color: var(--color-bg);
        }
        main {
            display: flex;
            flex-grow: 1;
            position: relative;
            overflow: hidden;
        }
        .canvas-container {
            flex-grow: 1;
            position: relative;
        }
        #schema-graph {
            display: block;
            width: 100%;
            height: 100%;
            cursor: grab;
        }
        #schema-graph:active { cursor: grabbing; }
        
        #side-panel {
            width: var(--sidepanel-width);
            flex-shrink: 0;
            background-color: var(--card-color);
            border-left: 1px solid var(--border-color);
            overflow-y: auto;
            padding: 16px;
            box-sizing: border-box;
            transition: transform 0.3s ease;
            position: absolute;
            right: 0;
            top: 0;
            bottom: 0;
            z-index: 5;
        }
        #side-panel.hidden {
            transform: translateX(100%);
        }
        #panel-toggle {
            position: absolute;
            top: 16px;
            right: calc(var(--sidepanel-width) + 16px);
            z-index: 6;
            background-color: var(--card-color);
            color: var(--text-color);
            border: 1px solid var(--border-color);
            border-radius: 50%;
            width: 32px;
            height: 32px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: right 0.3s ease;
        }
        #panel-toggle.panel-hidden {
            right: 16px;
        }
        .panel-header {
            margin-bottom: 16px;
        }
        .panel-header h2 {
            font-size: 18px;
            margin: 0 0 4px 0;
            word-break: break-all;
        }
        .panel-header .sub-name {
            font-size: 13px;
            color: var(--text-muted-color);
        }
        .badge {
            display: inline-block;
            padding: 3px 8px;
            font-size: 12px;
            font-weight: 500;
            border-radius: 12px;
            color: #fff;
        }
        .panel-section h3 {
            font-size: 14px;
            color: var(--text-muted-color);
            margin: 16px 0 8px 0;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 4px;
        }
        .panel-content p {
            font-size: 14px;
            line-height: 1.5;
            margin: 0;
        }
        .column-list {
            list-style: none;
            padding: 0;
            margin: 0;
            font-size: 13px;
        }
        .column-list li {
            display: flex;
            align-items: center;
            padding: 6px 0;
            border-bottom: 1px solid var(--border-color);
        }
        .column-list li:last-child { border-bottom: none; }
        .col-name { font-family: monospace; }
        .col-type {
            color: var(--text-muted-color);
            margin-left: auto;
            background-color: var(--bg-color);
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 12px;
        }
        .col-icon { margin-right: 6px; font-size: 12px; }
        .enum-pills { margin-top: 8px; display: flex; flex-wrap: wrap; gap: 6px; }
        .enum-pill {
            background-color: var(--bg-color);
            border: 1px solid var(--border-color);
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 12px;
            font-family: monospace;
        }
        .link-list li {
            padding: 4px 0;
            cursor: pointer;
            color: var(--accent-color);
        }
        .link-list li:hover { text-decoration: underline; }
        .info-grid { display: grid; grid-template-columns: 100px 1fr; gap: 8px; font-size: 14px; }
        .info-grid dt { color: var(--text-muted-color); }
        .info-grid dd { margin: 0; }

        footer {
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            padding: 8px 16px;
            background-color: rgba(15, 15, 19, 0.8);
            font-size: 12px;
            color: var(--text-muted-color);
            text-align: left;
            z-index: 5;
            box-sizing: border-box;
        }

        .node { cursor: pointer; }
        .node .node-rect { transition: stroke-width 0.2s; }
        .node:hover .node-rect { stroke-width: 3px; }
        .node .node-label {
            font-size: 12px;
            fill: var(--text-color);
            pointer-events: none;
            text-anchor: middle;
            dominant-baseline: middle;
        }
        .node .node-label-ko { }
        .node .node-label-id { font-size: 10px; fill: var(--text-muted-color); }
        .node .node-label-cols { display: none; font-size: 10px; fill: var(--accent-color); }

        .node.external .node-label-ko { }
        .node.external .node-polygon {
            stroke-width: 1.5px;
            stroke-dasharray: 4 2;
        }
        .node.tier-1 .node-polygon { fill: #f59e0b20; stroke: var(--tier1-color); }
        .node.tier-2 .node-polygon { fill: #84cc1620; stroke: var(--tier2-color); }
        .node.tier-3 .node-polygon { fill: #6366f120; stroke: var(--tier3-color); }

        .link {
            stroke-opacity: 0.6;
            transition: stroke-opacity 0.2s, stroke 0.2s;
            pointer-events: visibleStroke;
            cursor: default;
        }
        .link.internal { stroke: rgba(255,255,255,0.2); }
        .link.cross-dataset { stroke: rgba(255,255,255,0.5); stroke-dasharray: 5 5; }
        .link.external {
            stroke: var(--accent-color);
            stroke-width: 1.5px;
            stroke-dasharray: 8;
            animation: dash 5s linear infinite;
        }
        
        .node.dimmed, .link.dimmed { opacity: 0.1; }
        .node.highlighted .node-rect { stroke-width: 3px; }
        .link.highlighted { stroke-opacity: 1; stroke-width: 2.5px; }
        .node .node-rect.isolated { stroke-dasharray: 4 3; stroke-opacity: 0.5; fill-opacity: 0.5; }
        .node.isolated-node .node-label { fill-opacity: 0.6; }
        .dataset-hull { pointer-events: none; transition: opacity 0.3s; }

        .dataset-label {
            font-size: 16px;
            font-weight: bold;
            fill: var(--text-muted-color);
            text-anchor: middle;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.3s;
        }

        .minimap {
            position: absolute;
            bottom: 30px;
            right: 16px;
            width: 180px;
            height: 120px;
            background-color: var(--card-color);
            border: 1px solid var(--border-color);
            border-radius: 4px;
            overflow: hidden;
            z-index: 5;
        }
        .minimap svg {
            background-color: var(--bg-color);
        }
        .minimap .view-rect {
            fill: rgba(59, 130, 246, 0.3);
            stroke: var(--accent-color);
            stroke-width: 1px;
        }
        .zoom-controls {
            position: absolute;
            bottom: 160px;
            right: 16px;
            display: flex;
            flex-direction: column;
            gap: 1px;
            z-index: 5;
        }
        .zoom-controls button {
            width: 28px;
            height: 28px;
            background-color: var(--card-color);
            border: 1px solid var(--border-color);
            color: var(--text-color);
            cursor: pointer;
        }
        .zoom-controls button:first-child { border-radius: 4px 4px 0 0; }
        .zoom-controls button:last-child { border-radius: 0 0 4px 4px; }
        .zoom-controls button:hover { background-color: #2a2a2f; }

        .legend-panel { position: fixed; right: 12px; bottom: 12px; z-index: 100; background: var(--card-color); border: 1px solid var(--border-color); border-radius: 8px; min-width: 190px; box-shadow: 0 2px 8px rgba(0,0,0,0.3); transition: right 0.3s ease; }
        .legend-toggle { width: 100%; padding: 8px 12px; background: none; border: none; color: var(--text-color); cursor: pointer; font-size: 13px; text-align: left; display: flex; justify-content: space-between; align-items: center; }
        .legend-body { padding: 4px 12px 10px; display: none; }
        .legend-body.open { display: block; }
        .legend-section { font-size: 10px; color: var(--secondary-text); margin: 6px 0 3px; font-weight: 700; letter-spacing: 0.05em; text-transform: uppercase; }
        .legend-item { display: flex; align-items: center; gap: 8px; font-size: 12px; margin: 3px 0; color: var(--text-color); }
        .l-line { flex-shrink: 0; }
        .l-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }

    </style>
</head>
<body>
    <header>
        <h1>BigQuery 스키마 관계도</h1>
        <div class="controls">
            <div class="filter-group" id="tier-filters">
                <span class="group-label">Tier:</span>
            </div>
            <div class="filter-group" id="dataset-filters">
                <span class="group-label">Dataset:</span>
            </div>
            <div class="search-container">
                <input type="text" id="search-input" placeholder="검색...">
                <select id="search-select">
                    <option value="table_ko">테이블명(한)</option>
                    <option value="table_id">테이블명(영)</option>
                    <option value="column">컬럼명</option>
                </select>
            </div>
        </div>
    </header>
    <main>
        <div class="canvas-container">
            <svg id="schema-graph"></svg>
            <div class="zoom-controls">
                <button id="zoom-in">+</button>
                <button id="zoom-out">-</button>
            </div>
            <div class="minimap" id="minimap"></div>
            <div class="legend-panel" id="legend-panel">
                <button class="legend-toggle" id="legend-toggle">범례 <span id="legend-arrow">▲</span></button>
                <div class="legend-body open" id="legend-body">
                    <div class="legend-section">관계선</div>
                    <div class="legend-item"><svg class="l-line" width="28" height="10"><line x1="0" y1="5" x2="28" y2="5" stroke="rgba(255,255,255,0.5)" stroke-width="1.5"/><polygon points="20,2 28,5 20,8" fill="rgba(255,255,255,0.7)"/></svg>내부 관계</div>
                    <div class="legend-item"><svg class="l-line" width="28" height="10"><line x1="0" y1="5" x2="28" y2="5" stroke="rgba(255,255,255,0.5)" stroke-width="1.5" stroke-dasharray="4,3"/><polygon points="20,2 28,5 20,8" fill="rgba(255,255,255,0.7)"/></svg>데이터셋 간</div>
                    <div class="legend-item"><svg class="l-line" width="28" height="10"><line x1="0" y1="5" x2="28" y2="5" stroke="#60a5fa" stroke-width="1.5" stroke-dasharray="6,3"/><polygon points="20,2 28,5 20,8" fill="#60a5fa"/></svg>외부 시스템</div>
                    <div class="legend-section">노드</div>
                    <div class="legend-item"><svg class="l-line" width="20" height="14"><rect x="1" y="2" width="18" height="10" rx="2" fill="none" stroke="rgba(255,255,255,0.6)" stroke-width="1.5"/></svg>테이블</div>
                    <div class="legend-item"><svg class="l-line" width="20" height="14"><polygon points="10,1 19,7 10,13 1,7" fill="none" stroke="#60a5fa" stroke-width="1.5"/></svg>외부 시스템</div>
                    <div class="legend-item"><svg class="l-line" width="20" height="14"><rect x="1" y="2" width="18" height="10" rx="2" fill="none" stroke="rgba(255,255,255,0.3)" stroke-width="1.5" stroke-dasharray="3,2"/></svg>연결 없음</div>
                    <div class="legend-section">데이터셋</div>
                    <div id="legend-datasets"></div>
                </div>
            </div>
        </div>
        <div id="side-panel" class="hidden"></div>
        <button id="panel-toggle" class="panel-hidden">&lt;</button>
    </main>
    <footer>
        <span id="footer-stats"></span> |
        <span>Generated at: __GENERATED_AT__</span>
    </footer>

    <script>

        // --- 인라인 D3.js v7 라이브러리 ---
        __D3_SCRIPT__
        // ------------------------------------

        const graphData = __JSON_DATA__;

        // --- 초기 설정 ---
        const width = window.innerWidth;
        const height = window.innerHeight - document.querySelector('header').offsetHeight;
        
        const nodes = [...graphData.tables, ...graphData.external_nodes, ...graphData.dataset_nodes];
        const links = graphData.edges;

        // 데이터셋별 테이블 수 계산 → 각도 비례 배분
        const dsTableCounts = new Map();
        graphData.tables.forEach(t => {
            dsTableCounts.set(t.dataset_id, (dsTableCounts.get(t.dataset_id) || 0) + 1);
        });
        const dsNodes = graphData.dataset_nodes;
        const totalTables = graphData.tables.length || 1;
        const clusterRadius = Math.min(width, height) * 0.45;

        // 각 데이터셋에 테이블 수 비례 각도 할당 (최소 15° 보장)
        const minAngle = Math.PI / 12; // 15°
        const totalMinAngle = minAngle * dsNodes.length;
        const remainAngle = 2 * Math.PI - totalMinAngle;

        let currentAngle = -Math.PI / 2;
        dsNodes.forEach((d) => {
            const count = dsTableCounts.get(d.dataset_id) || 1;
            const proportionalAngle = minAngle + remainAngle * (count / totalTables);
            const midAngle = currentAngle + proportionalAngle / 2;
            d.x = Math.cos(midAngle) * clusterRadius;
            d.y = Math.sin(midAngle) * clusterRadius;
            d.fx = d.x;
            d.fy = d.y;
            currentAngle += proportionalAngle;
        });

        // 테이블 노드를 소속 앵커 근처에 테이블 수 비례 반경으로 초기 배치
        const dsAnchorMap = new Map(dsNodes.map(d => [d.dataset_id, d]));
        graphData.tables.forEach(t => {
            const anchor = dsAnchorMap.get(t.dataset_id);
            if (anchor) {
                const count = dsTableCounts.get(t.dataset_id) || 1;
                const scatter = Math.min(80 + Math.sqrt(count) * 55, 600);
                if (t.isIsolated) {
                    // 관계 없는 테이블은 클러스터 외곽 호(arc)에 배치
                    const isolatedInDs = graphData.tables.filter(n => n.isIsolated && n.dataset_id === t.dataset_id);
                    const idx = isolatedInDs.indexOf(t);
                    const total = isolatedInDs.length;
                    const arcAngle = Math.atan2(anchor.fy || anchor.y, anchor.fx || anchor.x);
                    const startAngle = arcAngle - Math.PI / 6;
                    const angle = startAngle + (Math.PI / 3) * (idx / Math.max(total - 1, 1));
                    t.x = (anchor.fx || anchor.x) + Math.cos(angle) * scatter * 0.85;
                    t.y = (anchor.fy || anchor.y) + Math.sin(angle) * scatter * 0.85;
                } else {
                    t.x = (anchor.fx || anchor.x) + (Math.random() - 0.5) * scatter;
                    t.y = (anchor.fy || anchor.y) + (Math.random() - 0.5) * scatter;
                }
            }
        });

        // 외부 시스템 초기 배치: 연결된 데이터셋 앵커 평균 위치 바깥쪽
        const isolatedExternals = graphData.external_nodes.filter(e => (e.connected_datasets || []).length === 0);
        graphData.external_nodes.forEach(ext => {
            const connDs = ext.connected_datasets || [];
            if (connDs.length > 0) {
                let avgX = 0, avgY = 0, cnt = 0;
                connDs.forEach(dsId => {
                    const anchor = dsAnchorMap.get(dsId);
                    if (anchor) { avgX += (anchor.fx || anchor.x); avgY += (anchor.fy || anchor.y); cnt++; }
                });
                if (cnt > 0) {
                    avgX /= cnt; avgY /= cnt;
                    const angle = Math.atan2(avgY, avgX);
                    const dist = Math.sqrt(avgX * avgX + avgY * avgY);
                    ext.x = avgX + Math.cos(angle) * Math.max(130, dist * 0.4);
                    ext.y = avgY + Math.sin(angle) * Math.max(130, dist * 0.4);
                }
            } else {
                // 연결 데이터셋 없는 외부 시스템: 외곽 원 균등 배치
                const idx = isolatedExternals.indexOf(ext);
                const total = isolatedExternals.length;
                const angle = -Math.PI / 2 + (2 * Math.PI * idx / Math.max(total, 1));
                const outerRadius = clusterRadius * 1.6;
                ext.x = Math.cos(angle) * outerRadius;
                ext.y = Math.sin(angle) * outerRadius;
            }
        });

        if (nodes.length === 0) {
            document.querySelector('main').innerHTML = '<div style="display:flex;align-items:center;justify-content:center;height:100%;color:#aaa;font-size:1.2rem;"><p>표시할 데이터가 없습니다. schema_config.py 설정을 확인해 주세요.</p></div>';
            throw new Error('No graph data');
        }

        const nodeMap = new Map(nodes.map(d => [d.id, d]));
        const validLinks = links.filter(link => {
            link.source = nodeMap.get(link.source);
            link.target = nodeMap.get(link.target);
            return link.source && link.target;
        });

        // 관계 없는 테이블 감지
        const connectedNodeIds = new Set();
        validLinks.forEach(l => {
            connectedNodeIds.add(l.source.id || l.source);
            connectedNodeIds.add(l.target.id || l.target);
        });
        graphData.tables.forEach(t => { t.isIsolated = !connectedNodeIds.has(t.id); });

        // 노드별 연결 수 계산 → 크기 가변 (E)
        const _connCount = new Map();
        validLinks.forEach(l => {
            _connCount.set(l.source.id, (_connCount.get(l.source.id) || 0) + 1);
            _connCount.set(l.target.id, (_connCount.get(l.target.id) || 0) + 1);
        });
        graphData.tables.forEach(t => {
            t.connections = _connCount.get(t.id) || 0;
            t._w = 130 + Math.min(t.connections, 8) * 8;
            t._h = 36 + Math.min(t.connections, 8) * 2;
        });

        const tierColors = {
            1: 'var(--tier1-color)',
            2: 'var(--tier2-color)',
            3: 'var(--tier3-color)',
        };

        let activeFilters = {
            datasets: new Set(Object.keys(graphData.datasets)),
            tiers: new Set([1, 2, 3]),
            search: ''
        };

        // --- SVG 및 시뮬레이션 설정 ---
        const svg = d3.select("svg#schema-graph")
            .attr("viewBox", [-width / 2, -height / 2, width, height]);

        const mainGroup = svg.append("g");
        
        // 화살표 마커 정의
        mainGroup.append("defs").selectAll("marker")
            .data(["end"])
            .join("marker")
            .attr("id", String)
            .attr("viewBox", "0 -5 10 10")
            .attr("refX", 10)
            .attr("refY", 0)
            .attr("markerWidth", 10)
            .attr("markerHeight", 10)
            .attr("orient", "auto")
            .append("path")
            .attr("d", "M0,-5L10,0L0,5")
            .attr("fill", "rgba(255,255,255,0.8)");

        const simulation = d3.forceSimulation(nodes)
            .force("link", d3.forceLink(validLinks).id(d => d.id)
                .distance(d => d.type === 'cross-dataset' ? 200 : (d.type === 'external' ? 160 : 100))
                .strength(d => d.type === 'cross-dataset' ? 0.3 : 0.7))
            .force("charge", d3.forceManyBody().strength(d => {
                if (d.type === 'dataset') return 0;
                if (d.type === 'external') return -150;
                return -350;
            }))
            .force("x", d3.forceX(0).strength(0.01))
            .force("y", d3.forceY(0).strength(0.01))
            .force("cluster", forceCluster())
            .force("collide", d3.forceCollide().radius(d => {
                if (d.type === 'table') return Math.sqrt((d._w||130)**2 + (d._h||36)**2) / 2 + 8;
                if (d.type === 'external') return 70;
                return 0;
            }).strength(0.8))
            .alphaDecay(0.02)
            .velocityDecay(0.3);

        // --- 요소 렌더링 ---
        // 데이터셋 경계 Hull (링크·노드 아래 레이어)
        const hullGroup = mainGroup.append("g").attr("class", "hulls");
        const hullPaths = hullGroup.selectAll("path")
            .data(graphData.dataset_nodes)
            .join("path")
            .attr("class", "dataset-hull")
            .attr("fill", d => d.color + "10")
            .attr("stroke", d => d.color + "30")
            .attr("stroke-width", 1.5)
            .attr("stroke-linejoin", "round");

        function updateHulls() {
            hullPaths.attr("d", d => {
                const clusterNodes = nodes.filter(n => n.type === 'table' && n.dataset_id === d.dataset_id);
                if (clusterNodes.length === 0) return null;
                if (clusterNodes.length === 1) {
                    const n = clusterNodes[0];
                    const pad = 35;
                    return `M${n.x - pad},${n.y - pad}L${n.x + pad},${n.y - pad}L${n.x + pad},${n.y + pad}L${n.x - pad},${n.y + pad}Z`;
                }
                const points = clusterNodes.map(n => [n.x, n.y]);
                const hull = d3.polygonHull(points);
                if (!hull) return null;
                const centroid = d3.polygonCentroid(hull);
                const pad = 45;
                const expanded = hull.map(p => {
                    const dx = p[0] - centroid[0];
                    const dy = p[1] - centroid[1];
                    const dist = Math.sqrt(dx * dx + dy * dy) || 1;
                    return [p[0] + dx / dist * pad, p[1] + dy / dist * pad];
                });
                return d3.line().curve(d3.curveCatmullRomClosed.alpha(0.8))(expanded);
            });
        }

        // 병렬 관계선 오프셋 계산 (겹침 방지, B)
        const _pairCount = new Map();
        validLinks.forEach(l => {
            const key = [l.source.id, l.target.id].sort().join('__');
            _pairCount.set(key, (_pairCount.get(key) || 0) + 1);
        });
        const _pairIdx = new Map();
        validLinks.forEach(l => {
            const key = [l.source.id, l.target.id].sort().join('__');
            const idx = _pairIdx.get(key) || 0;
            const cnt = _pairCount.get(key) || 1;
            l._offset = (idx - (cnt - 1) / 2) * 16;
            l._parallel = cnt;
            _pairIdx.set(key, idx + 1);
        });

        const link = mainGroup.append("g")
            .attr("class", "links")
            .selectAll("path")
            .data(validLinks)
            .join("path")
            .attr("class", d => `link ${d.type}`)
            .attr("fill", "none")
            .attr("marker-end", "url(#end)");

        link.append("title").text(d => [d.rel, d.description].filter(Boolean).join(' | '));

        const node = mainGroup.append("g")
            .attr("class", "nodes")
            .selectAll("g")
            .data(nodes.filter(d => d.type !== 'dataset')) // 데이터셋 앵커 노드는 그리지 않음
            .join("g")
            .attr("class", d => `node ${d.type} ${d.tier ? `tier-${d.tier}` : ''}`)
            .call(drag(simulation));

        // 테이블 노드 (rect)
        node.filter(d => d.type === 'table').append("rect")
            .attr("width", d => d._w || 130)
            .attr("height", d => d._h || 36)
            .attr("x", d => -((d._w || 130) / 2))
            .attr("y", d => -((d._h || 36) / 2))
            .attr("rx", 8)
            .attr("class", d => `node-rect${d.isIsolated ? ' isolated' : ''}`)
            .attr("fill", d => d.dataset_meta.color + '20')
            .attr("stroke", d => d.dataset_meta.color);

        // 외부 시스템 노드 (polygon, 다이아몬드)
        node.filter(d => d.type === 'external').append("polygon")
            .attr("points", "0,-25 60,0 0,25 -60,0")
            .attr("class", "node-polygon");
            
        // 노드 레이블
        const labels = node.append("text").attr("class", "node-label");
        
        labels.append("tspan") // 한글 이름
            .attr("class", "node-label-ko")
            .attr("x", 0)
            .attr("dy", d => d.type === 'table' ? "-0.4em" : "0.35em")
            .text(d => d.name_ko);

        labels.filter(d => d.type === 'table').append("tspan") // 영문 ID
            .attr("class", "node-label-id")
            .attr("x", 0)
            .attr("dy", "1.2em")
            .text(d => d.table_id);

        labels.filter(d => d.type === 'table').append("tspan") // 컬럼 수
            .attr("class", "node-label-cols")
            .attr("x", 0)
            .attr("dy", "1.2em")
            .text(d => `${d.column_count} columns`);

        // 데이터셋 레이블
        const datasetLabels = mainGroup.append("g")
            .attr("class", "dataset-labels")
            .selectAll("text")
            .data(graphData.dataset_nodes)
            .join("text")
            .attr("class", "dataset-label")
            .style("fill", d => d.color)
            .text(d => d.label_ko);

        // --- 줌/팬 설정 ---
        const zoom = d3.zoom()
            .scaleExtent([0.1, 4])
            .on("zoom", zoomed);
        
        svg.call(zoom);
        svg.on("dblclick.zoom", null);

        function zoomed({transform}) {
            mainGroup.attr("transform", transform);
            updateMinimapViewRect(transform);

            const k = transform.k;
            node.select(".node-label-cols").style("display", k > 1.0 ? "inline" : "none");
            datasetLabels.style("opacity", k < 0.7 ? Math.min(0.85, (0.7 - k) / 0.3 + 0.1) : 0);
            hullPaths.style("opacity", Math.max(0.4, Math.min(1.0, 1.5 - k)));
            node.selectAll(".node-label").style("display", k < 0.2 ? "none" : null);
        }

        // --- 시뮬레이션 tick ---
        simulation.on("tick", () => {
            link.attr("d", d => {
                const sx = d.source.x, sy = d.source.y;
                const tx = d.target.x, ty = d.target.y;
                const dx = tx - sx, dy = ty - sy;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist === 0) return '';
                const nw = d.target._w || (d.target.type === 'table' ? 130 : 120);
                const nh = d.target._h || (d.target.type === 'table' ? 36 : 50);
                const r = Math.min(Math.abs(nw / 2 / dx), Math.abs(nh / 2 / dy));
                const ex = tx - dx * r, ey = ty - dy * r;
                if (!d._offset || d._parallel <= 1) return `M${sx},${sy} L${ex},${ey}`;
                const cx = (sx + ex) / 2 + (dy / dist) * d._offset;
                const cy = (sy + ey) / 2 - (dx / dist) * d._offset;
                return `M${sx},${sy} Q${cx},${cy} ${ex},${ey}`;
            });

            node.attr("transform", d => `translate(${d.x}, ${d.y})`);

            datasetLabels
                .attr("x", d => {
                    const ns = nodes.filter(n => n.type === 'table' && n.dataset_id === d.dataset_id);
                    return ns.length ? ns.reduce((s, n) => s + n.x, 0) / ns.length : d.x;
                })
                .attr("y", d => {
                    const ns = nodes.filter(n => n.type === 'table' && n.dataset_id === d.dataset_id);
                    return ns.length ? Math.min(...ns.map(n => n.y)) - 28 : d.y;
                });

            updateHulls();
        });

        // 시뮬레이션 안정화 후 전체 그래프 화면 자동 맞춤 (최초 1회만)
        let initialFitDone = false;
        simulation.on("end", () => {
            updateMinimap();
            if (initialFitDone) return;
            initialFitDone = true;
            try {
                const visibleNodes = nodes.filter(n => n.type === 'table');
                if (!visibleNodes.length) return;

                // IQR 기반 outlier 제거 — 메인 클러스터에 포커스
                const sorted = (arr) => [...arr].sort((a, b) => a - b);
                const q = (arr, p) => arr[Math.floor(arr.length * p)];
                const xs = sorted(visibleNodes.map(n => n.x));
                const ys = sorted(visibleNodes.map(n => n.y));
                const xQ1 = q(xs, 0.25), xQ3 = q(xs, 0.75), xIQR = xQ3 - xQ1;
                const yQ1 = q(ys, 0.25), yQ3 = q(ys, 0.75), yIQR = yQ3 - yQ1;
                const coreNodes = visibleNodes.filter(n =>
                    n.x >= xQ1 - 1.5 * xIQR && n.x <= xQ3 + 1.5 * xIQR &&
                    n.y >= yQ1 - 1.5 * yIQR && n.y <= yQ3 + 1.5 * yIQR
                );
                const fitNodes = coreNodes.length > 0 ? coreNodes : visibleNodes;

                let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
                fitNodes.forEach(n => {
                    minX = Math.min(minX, n.x - 70);
                    maxX = Math.max(maxX, n.x + 70);
                    minY = Math.min(minY, n.y - 25);
                    maxY = Math.max(maxY, n.y + 25);
                });
                const pad = 80;
                const bw = (maxX - minX) + 2 * pad;
                const bh = (maxY - minY) + 2 * pad;
                const scale = Math.min(width / bw, height / bh, 1.0);
                const cx = (minX + maxX) / 2;
                const cy = (minY + maxY) / 2;
                svg.transition().duration(1000).call(
                    zoom.transform,
                    d3.zoomIdentity.scale(scale).translate(-cx, -cy)
                );
            } catch (e) {}
        });

        // --- 커스텀 클러스터 Force ---
        function forceCluster() {
            let allNodes;
            const clusterAnchors = new Map(graphData.dataset_nodes.map(d => [d.dataset_id, d]));

            // 외부 시스템 타깃 위치 사전 계산
            const externalTargets = new Map();
            graphData.external_nodes.forEach(ext => {
                const connDs = ext.connected_datasets || [];
                if (connDs.length > 0) {
                    let avgX = 0, avgY = 0, cnt = 0;
                    connDs.forEach(dsId => {
                        const anchor = clusterAnchors.get(dsId);
                        if (anchor) { avgX += (anchor.fx || anchor.x); avgY += (anchor.fy || anchor.y); cnt++; }
                    });
                    if (cnt > 0) {
                        avgX /= cnt; avgY /= cnt;
                        const angle = Math.atan2(avgY, avgX);
                        const dist = Math.sqrt(avgX * avgX + avgY * avgY);
                        externalTargets.set(ext.id, { x: avgX + Math.cos(angle) * Math.max(130, dist * 0.4), y: avgY + Math.sin(angle) * Math.max(130, dist * 0.4) });
                    }
                }
            });

            function force(alpha) {
                for (const n of allNodes) {
                    if (n.type === 'table') {
                        const anchor = clusterAnchors.get(n.dataset_id);
                        if (!anchor || anchor === n) continue;
                        const count = dsTableCounts.get(n.dataset_id) || 1;
                        // 클러스터 크기에 따라 인력 약화 (40개=0.1, 3개=0.56)
                        const strength = Math.max(0.1, 0.6 - count / 80);
                        n.vx -= (n.x - (anchor.fx || anchor.x)) * strength * alpha;
                        n.vy -= (n.y - (anchor.fy || anchor.y)) * strength * alpha;
                    } else if (n.type === 'external') {
                        const target = externalTargets.get(n.id);
                        if (target) {
                            n.vx -= (n.x - target.x) * 0.3 * alpha;
                            n.vy -= (n.y - target.y) * 0.3 * alpha;
                        }
                    }
                }
            }
            force.initialize = _ => allNodes = _;
            return force;
        }

        // --- 드래그 핸들러 ---
        function drag(simulation) {
            function dragstarted(event, d) {
                if (d.type === 'external') return;
                if (!event.active) simulation.alphaTarget(0.3).restart();
                d.fx = d.x;
                d.fy = d.y;
            }
            function dragged(event, d) {
                if (d.type === 'external') return;
                d.fx = event.x;
                d.fy = event.y;
            }
            function dragended(event, d) {
                if (!event.active) simulation.alphaTarget(0);
            }
            return d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended);
        }
        node.on("dblclick", (event, d) => {
            event.stopPropagation();
            if (d.type === 'external') return;
            d.fx = null;
            d.fy = null;
        });

        // --- 상호작용: 호버, 클릭 ---
        node.on("mouseover", handleMouseOver)
            .on("mouseout", handleMouseOut)
            .on("click", handleClick);

        const allNodes = mainGroup.selectAll(".node");
        const allLinks = mainGroup.selectAll(".link");
        let pinnedNode = null;

        function applyHighlight(d) {
            allNodes.classed("dimmed", true);
            allLinks.classed("dimmed", true);
            const connectedNodes = new Set([d.id]);
            validLinks.forEach(l => {
                if (l.source.id === d.id) connectedNodes.add(l.target.id);
                if (l.target.id === d.id) connectedNodes.add(l.source.id);
            });
            allNodes.filter(n => connectedNodes.has(n.id)).classed("dimmed", false).classed("highlighted", true);
            allLinks.filter(l => (l.source.id === d.id || l.target.id === d.id)).classed("dimmed", false).classed("highlighted", true);
        }

        function clearHighlight() {
            allNodes.classed("dimmed", false).classed("highlighted", false);
            allLinks.classed("dimmed", false).classed("highlighted", false);
        }

        function handleMouseOver(event, d) {
            if (pinnedNode) return;
            applyHighlight(d);
        }

        function handleMouseOut() {
            if (pinnedNode) return;
            clearHighlight();
        }

        function handleClick(event, d) {
            if (event) event.stopPropagation();
            updateSidePanel(d);
            document.getElementById('side-panel').classList.remove('hidden');
            document.getElementById('panel-toggle').classList.remove('panel-hidden');
            document.getElementById('panel-toggle').innerHTML = '&gt;';
            document.getElementById('legend-panel').style.right = 'calc(var(--sidepanel-width) + 12px)';
            if (pinnedNode && pinnedNode.id === d.id) {
                pinnedNode = null;
                clearHighlight();
            } else {
                pinnedNode = d;
                applyHighlight(d);
            }
        }

        svg.on("click", () => {
            if (pinnedNode) {
                pinnedNode = null;
                clearHighlight();
            }
        });

        // --- 범례 ---
        document.getElementById('legend-toggle').addEventListener('click', () => {
            const body = document.getElementById('legend-body');
            const arrow = document.getElementById('legend-arrow');
            body.classList.toggle('open');
            arrow.textContent = body.classList.contains('open') ? '▲' : '▼';
        });
        const legendDs = document.getElementById('legend-datasets');
        Object.values(graphData.datasets).forEach(ds => {
            const item = document.createElement('div');
            item.className = 'legend-item';
            item.innerHTML = `<span class="l-dot" style="background:${ds.color};"></span>${ds.label_ko}`;
            legendDs.appendChild(item);
        });

        // --- 사이드 패널 ---
        const sidePanel = document.getElementById('side-panel');
        const panelToggle = document.getElementById('panel-toggle');
        const legendPanel = document.getElementById('legend-panel');

        function updateLegendPosition() {
            const isHidden = sidePanel.classList.contains('hidden');
            legendPanel.style.right = isHidden ? '12px' : 'calc(var(--sidepanel-width) + 12px)';
        }

        panelToggle.addEventListener('click', () => {
            sidePanel.classList.toggle('hidden');
            panelToggle.classList.toggle('panel-hidden');
            panelToggle.innerHTML = sidePanel.classList.contains('hidden') ? '&lt;' : '&gt;';
            updateLegendPosition();
        });
        
        function updateSidePanel(d) {
            if (!d) {
                sidePanel.innerHTML = '<p>노드를 클릭하여 상세 정보를 확인하세요.</p>';
                return;
            }

            let content = '';
            if (d.type === 'table') {
                const dsMeta = d.dataset_meta;
                const badge = `<span class="badge" style="background-color: ${dsMeta.color};">${dsMeta.label_ko}</span>`;
                const connectedLinks = validLinks.filter(l => l.source.id === d.id || l.target.id === d.id);

                content = `
                    <div class="panel-header">
                        <h2>${d.name_ko} ${badge}</h2>
                        <p class="sub-name">${d.id}</p>
                    </div>
                    <div class="panel-section">
                        <h3>설명</h3>
                        <div class="panel-content"><p>${d.description || '설명 없음'}</p></div>
                    </div>
                    <div class="panel-section">
                        <h3>컬럼 (${d.column_count})</h3>
                        <ul class="column-list">
                            ${d.columns.map(c => `
                                <li>
                                    ${c.pk ? '<span class="col-icon" title="Primary Key">🔑</span>' : ''}
                                    ${c.fk ? '<span class="col-icon" title="Foreign Key">🔗</span>' : ''}
                                    <span class="col-name">${c.name}</span>
                                    <span class="col-type">${c.type}</span>
                                </li>
                                ${c.enum ? `<li style="border-top:1px dashed var(--border-color);"><div class="enum-pills">${c.enum.map(e => `<div class="enum-pill">${e}</div>`).join('')}</div></li>` : ''}
                            `).join('')}
                        </ul>
                    </div>
                     <div class="panel-section">
                        <h3>연결된 테이블/시스템</h3>
                        <ul class="column-list link-list">
                            ${connectedLinks.map(l => {
                                const targetNode = l.source.id === d.id ? l.target : l.source;
                                return `<li onclick="focusOnNode('${targetNode.id}')">${targetNode.name_ko} (${targetNode.id})</li>`;
                            }).join('')}
                        </ul>
                    </div>
                `;
            } else if (d.type === 'external') {
                const connectedDatasets = new Set();
                 validLinks.filter(l => l.source.id === d.id || l.target.id === d.id)
                      .forEach(l => {
                          const tableNode = l.source.id === d.id ? l.target : l.source;
                          if (tableNode.dataset_id) connectedDatasets.add(tableNode.dataset_id);
                      });

                content = `
                    <div class="panel-header">
                        <h2>${d.name_ko}</h2>
                        <p class="sub-name">외부 연동 시스템</p>
                    </div>
                    <div class="panel-section">
                        <h3>시스템 정보</h3>
                        <dl class="info-grid">
                            <dt>Tier</dt><dd><span class="badge" style="background-color: ${tierColors[d.tier]}">Tier ${d.tier}</span></dd>
                            <dt>동기화 방식</dt><dd>${d.sync_type || 'N/A'}</dd>
                            ${d.sync_frequency ? `<dt>동기화 주기</dt><dd>${d.sync_frequency}</dd>` : ''}
                            <dt>데이터 방향</dt><dd>${d.sync_direction || 'N/A'}</dd>
                        </dl>
                    </div>
                    <div class="panel-section">
                        <h3>연결된 데이터셋</h3>
                        <div class="enum-pills">
                            ${[...connectedDatasets].filter(dsId => dsId && graphData.datasets[dsId]).map(dsId => {
                                const dsMeta = graphData.datasets[dsId];
                                return `<span class="badge" style="background-color: ${dsMeta.color}; cursor: pointer;" onclick="toggleDatasetFilter('${dsId}', true)">${dsMeta.label_ko}</span>`;
                            }).join('')}
                        </div>
                    </div>
                `;
            }
            sidePanel.innerHTML = content;
        }

        function focusOnNode(nodeId) {
            const targetNode = nodeMap.get(nodeId);
            if (!targetNode) return;
            
            const k = 1.2;
            const transform = d3.zoomIdentity
                .scale(k)
                .translate(-targetNode.x, -targetNode.y);

            svg.transition().duration(750).call(zoom.transform, transform);
            handleClick(null, targetNode);
        }
        window.focusOnNode = focusOnNode;

        // --- 필터링 및 검색 ---
        const searchInput = document.getElementById('search-input');
        const searchSelect = document.getElementById('search-select');
        searchInput.addEventListener('input', () => {
            activeFilters.search = searchInput.value.toLowerCase();
            applyFilters();
        });
        searchSelect.addEventListener('change', applyFilters);

        function applyFilters() {
            const searchTerm = activeFilters.search;
            const searchField = searchSelect.value;
            
            allNodes.style('display', d => {
                let isVisible = true;

                if (d.type === 'table') {
                    if (!activeFilters.datasets.has(d.dataset_id)) {
                        isVisible = false;
                    }
                    if (searchTerm) {
                        let match = false;
                        if (searchField === 'table_ko') {
                            match = d.name_ko.toLowerCase().includes(searchTerm);
                        } else if (searchField === 'table_id') {
                            match = d.id.toLowerCase().includes(searchTerm);
                        } else if (searchField === 'column') {
                            match = d.columns.some(c => c.name.toLowerCase().includes(searchTerm));
                        }
                        if (!match) isVisible = false;
                    }
                } else if (d.type === 'external') {
                    if (!activeFilters.tiers.has(d.tier)) {
                        isVisible = false;
                    }
                }
                return isVisible ? null : 'none';
            });

            allLinks.style('display', d => {
                 const sourceVisible = allNodes.filter(n => n.id === d.source.id).style('display') !== 'none';
                 const targetVisible = allNodes.filter(n => n.id === d.target.id).style('display') !== 'none';
                 return (sourceVisible && targetVisible) ? null : 'none';
            });
        }
        
        // 데이터셋 필터 버튼 생성
        const datasetFiltersContainer = document.getElementById('dataset-filters');
        Object.entries(graphData.datasets).forEach(([id, meta]) => {
            const btn = document.createElement('button');
            btn.className = 'filter-btn active';
            btn.textContent = meta.label_ko;
            btn.dataset.filter = id;
            btn.style.setProperty('--color', meta.color);
            btn.style.setProperty('--color-bg', meta.color + '40');
            btn.addEventListener('click', () => toggleDatasetFilter(id));
            datasetFiltersContainer.appendChild(btn);
        });
        
        function toggleDatasetFilter(datasetId, forceActive = false) {
            const btn = document.querySelector(`.filter-btn[data-filter="${datasetId}"]`);
            if (forceActive) {
                activeFilters.datasets.add(datasetId);
                btn.classList.add('active');
            } else {
                if (activeFilters.datasets.has(datasetId)) {
                    activeFilters.datasets.delete(datasetId);
                    btn.classList.remove('active');
                } else {
                    activeFilters.datasets.add(datasetId);
                    btn.classList.add('active');
                }
            }
            applyFilters();
        }
        window.toggleDatasetFilter = toggleDatasetFilter;

        // Tier 필터 버튼 생성
        const tierFiltersContainer = document.getElementById('tier-filters');
        [1, 2, 3].forEach(tier => {
            const btn = document.createElement('button');
            btn.className = 'filter-btn active';
            btn.textContent = `T${tier}`;
            btn.dataset.tier = tier;
            const color = tierColors[tier];
            btn.style.setProperty('--color', color);
            btn.style.setProperty('--color-bg', color.replace('var(','').replace(')','') + '40');
            btn.addEventListener('click', () => {
                if (activeFilters.tiers.has(tier)) {
                    activeFilters.tiers.delete(tier);
                    btn.classList.remove('active');
                } else {
                    activeFilters.tiers.add(tier);
                    btn.classList.add('active');
                }
                applyFilters();
            });
            tierFiltersContainer.appendChild(btn);
        });

        // --- 미니맵 ---
        const minimapContainer = d3.select("#minimap");
        const minimapSvg = minimapContainer.append("svg")
            .attr("width", "100%")
            .attr("height", "100%");

        const minimapNodes = minimapSvg.append("g")
            .selectAll("circle")
            .data(nodes.filter(d => d.type !== 'dataset'))
            .join("circle")
            .attr("r", 2)
            .attr("fill", d => d.type === 'table' ? d.dataset_meta.color : tierColors[d.tier]);
        
        const minimapViewRect = minimapSvg.append("rect").attr("class", "view-rect");
        
        let minimapScale;
        function updateMinimap() {
            const nodeBounds = mainGroup.node().getBBox();
            const minimapWidth = minimapContainer.node().clientWidth;
            const minimapHeight = minimapContainer.node().clientHeight;

            minimapScale = Math.min(
                minimapWidth / nodeBounds.width,
                minimapHeight / nodeBounds.height
            ) * 0.9;

            const tx = (minimapWidth - nodeBounds.width * minimapScale) / 2 - nodeBounds.x * minimapScale;
            const ty = (minimapHeight - nodeBounds.height * minimapScale) / 2 - nodeBounds.y * minimapScale;

            minimapNodes
                .attr("cx", d => d.x * minimapScale + tx)
                .attr("cy", d => d.y * minimapScale + ty);
            
            updateMinimapViewRect(d3.zoomTransform(svg.node()));
        }

        function updateMinimapViewRect(transform) {
            if (!minimapScale) return;
            const nodeBounds = mainGroup.node().getBBox();
            const minimapWidth = minimapContainer.node().clientWidth;
            const minimapHeight = minimapContainer.node().clientHeight;
            const tx = (minimapWidth - nodeBounds.width * minimapScale) / 2 - nodeBounds.x * minimapScale;
            const ty = (minimapHeight - nodeBounds.height * minimapScale) / 2 - nodeBounds.y * minimapScale;

            const svgWidth = svg.node().clientWidth;
            const svgHeight = svg.node().clientHeight;

            const viewX = (-transform.x / transform.k) * minimapScale + tx;
            const viewY = (-transform.y / transform.k) * minimapScale + ty;
            const viewWidth = (svgWidth / transform.k) * minimapScale;
            const viewHeight = (svgHeight / transform.k) * minimapScale;
            
            minimapViewRect
                .attr("x", viewX)
                .attr("y", viewY)
                .attr("width", viewWidth)
                .attr("height", viewHeight);
        }
        
        // 최초 로딩 후 미니맵 업데이트
        setTimeout(updateMinimap, 1000); // 시뮬레이션 안정화 시간

        // --- 줌 컨트롤 버튼 ---
        d3.select('#zoom-in').on('click', () => svg.transition().call(zoom.scaleBy, 1.2));
        d3.select('#zoom-out').on('click', () => svg.transition().call(zoom.scaleBy, 0.8));

        // --- 푸터 정보 업데이트 ---
        document.getElementById('footer-stats').textContent = 
            `테이블 ${graphData.tables.length}개 · 관계 ${graphData.edges.length}개 · 외부 시스템 ${graphData.external_nodes.length}개`;
    </script>
</body>
</html>
    """
    html_template = (html_template
        .replace('__GENERATED_AT__', graph_data['generated_at'])
        .replace('__D3_SCRIPT__', d3_script_content)
        .replace('__JSON_DATA__', json_data))
    print("HTML 파일 생성 완료.")
    return html_template

def main():
    """스크립트 실행 메인 함수"""
    output_filename = os.getenv('OUTPUT_HTML', 'index.html')
    
    # 1. BQ 스키마 조회
    bq_schemas = fetch_bq_schemas()
    if not bq_schemas:
        print("조회된 스키마가 없어 스크립트를 종료합니다.", file=sys.stderr)
        return

    # 2. 그래프 데이터 빌드
    graph_data = build_graph_data(bq_schemas)
    
    # 3. HTML 생성
    html_content = generate_html(graph_data)
    
    # 4. 파일 저장
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"\n성공! 스키마 그래프가 '{os.path.abspath(output_filename)}' 파일로 저장되었습니다.")
        print("웹 브라우저에서 해당 파일을 열어 확인하세요.")
    except IOError as e:
        print(f"오류: 파일 저장 실패. '{output_filename}' ({e})", file=sys.stderr)

if __name__ == '__main__':
    main()
