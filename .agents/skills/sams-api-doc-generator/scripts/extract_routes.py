#!/usr/bin/env python3
"""
SAMS API Route Extractor & Documentation Generator
Tự động quét các Flask Blueprints trong `backend/app/api/` sử dụng phân tích cú pháp tĩnh (Python AST)
và trích xuất định nghĩa endpoint để bổ sung vào tài liệu `API.md`.

Hoạt động hoàn toàn bằng Python Standard Library (ast, re, pathlib), không cần cài đặt thêm thư viện ngoài.
"""

import ast
import os
import sys
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

class RouteVisitor(ast.NodeVisitor):
    def __init__(self, filename: str):
        self.filename = filename
        self.routes: List[Dict[str, Any]] = []

    def visit_FunctionDef(self, node: ast.FunctionDef):
        route_info = self._extract_route(node)
        if route_info:
            self.routes.append(route_info)
        self.generic_visit(node)

    def _extract_route(self, node: ast.FunctionDef) -> Optional[Dict[str, Any]]:
        is_route = False
        rule_path = ""
        methods = ["GET"]
        auth_level = "Public"
        decorators_list = []

        for dec in node.decorator_list:
            dec_str = ast.unparse(dec) if hasattr(ast, "unparse") else ""
            decorators_list.append(dec_str)

            # Detect auth decorators
            if "admin_required" in dec_str:
                auth_level = "Admin"
            elif "landlord_required" in dec_str:
                auth_level = "Landlord"
            elif "tenant_required" in dec_str:
                auth_level = "Tenant"
            elif "jwt_required" in dec_str and auth_level == "Public":
                auth_level = "Authenticated"

            # Detect .route(...) or .endpoint(...)
            if isinstance(dec, ast.Call):
                func = dec.func
                func_name = getattr(func, "attr", "")
                if func_name in ("route", "post", "get", "put", "delete", "patch"):
                    is_route = True
                    # Extract path argument
                    if dec.args and isinstance(dec.args[0], ast.Constant):
                        rule_path = dec.args[0].value
                    elif dec.args and isinstance(dec.args[0], ast.Str): # Python < 3.8 compat
                        rule_path = dec.args[0].s

                    # Extract methods argument
                    for kw in dec.keywords:
                        if kw.arg == "methods" and isinstance(kw.value, (ast.List, ast.Tuple)):
                            methods = [
                                elt.value if isinstance(elt, ast.Constant) else getattr(elt, "s", "")
                                for elt in kw.value.elts
                            ]
                    if func_name in ("post", "get", "put", "delete", "patch"):
                        methods = [func_name.upper()]

        if not is_route:
            return None

        # Extract docstring
        docstring = ast.get_docstring(node) or ""
        
        # Analyze request arguments
        params = [arg.arg for arg in node.args.args if arg.arg not in ("self", "cls")]

        return {
            "name": node.name,
            "path": rule_path,
            "methods": methods,
            "auth": auth_level,
            "docstring": docstring.strip(),
            "params": params,
            "filename": self.filename,
            "line": node.lineno
        }

def scan_api_directory(api_dir: Path) -> List[Dict[str, Any]]:
    all_routes = []
    if not api_dir.exists():
        return all_routes

    for file_path in sorted(api_dir.glob("*.py")):
        if file_path.name.startswith("__"):
            continue
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                code = f.read()
            tree = ast.parse(code, filename=str(file_path))
            visitor = RouteVisitor(filename=file_path.name)
            visitor.visit(tree)
            all_routes.extend(visitor.routes)
        except Exception as e:
            print(f"⚠️ [Cảnh báo] Lỗi phân tích cú pháp file {file_path.name}: {e}", file=sys.stderr)

    return all_routes

def format_route_markdown(route: Dict[str, Any], base_prefix: str = "/api/v1") -> str:
    path = route["path"]
    full_path = f"{base_prefix}{path}" if not path.startswith(base_prefix) else path
    methods = ", ".join(route["methods"])
    primary_method = route["methods"][0] if route["methods"] else "GET"
    doc = route["docstring"] or f"Endpoint {route['name']}"

    # Extract summary and details from docstring
    lines = doc.split("\n")
    summary = lines[0].strip() if lines else f"Xử lý {route['name']}"
    description = "\n".join(lines[1:]).strip() if len(lines) > 1 else ""

    md = f"""#### `{primary_method}` {full_path}
- **Tên hàm Backend:** `{route['name']}()` (tại `{route['filename']}:{route['line']}`)
- **Mô tả:** {summary}
- **Quyền truy cập:** `{route['auth']}`
- **Phương thức hỗ trợ:** `{methods}`
"""
    if route["params"]:
        md += f"- **Tham số đường dẫn (Path Params):** `{', '.join(route['params'])}`\n"

    if description:
        md += f"\n**Chi tiết nghiệp vụ:**\n```text\n{description}\n```\n"

    md += """
- **Response Chuẩn:**
```json
{
  "success": true,
  "data": {},
  "meta": { "timestamp": "2026-10-01T12:00:00Z" },
  "error": null
}
```
---
"""
    return md

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Tự động trích xuất và sinh tài liệu API từ Backend Flask.")
    parser.add_argument("--api-dir", default="backend/app/api", help="Đường dẫn thư mục controllers (mặc định: backend/app/api)")
    parser.add_argument("--output", default="API.md", help="Tài liệu API đích (mặc định: API.md)")
    parser.add_argument("--check-only", action="store_true", help="Chỉ kiểm tra và liệt kê các routes tìm thấy")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[4]
    api_path = project_root / args.api_dir
    api_md_path = project_root / args.output

    if not api_path.exists():
        # Fallback relative to current working directory
        api_path = Path.cwd() / args.api_dir

    print(f"🔍 Đang quét mã nguồn Backend tại: {api_path}")
    routes = scan_api_directory(api_path)

    if not routes:
        print(f"ℹ️ Chưa tìm thấy route nào trong {api_path}. Có thể code Backend chưa được viết.")
        sys.exit(0)

    print(f"✅ Đã trích xuất thành công {len(routes)} endpoint từ mã nguồn Backend!")

    if args.check_only:
        print("\n📋 Danh sách Endpoints phát hiện được:")
        for r in routes:
            print(f"  [{', '.join(r['methods']):<6}] {r['path']:<35} -> {r['name']}() (Quyền: {r['auth']})")
        sys.exit(0)

    # Generate Markdown documentation
    generated_content = "\n## Các Endpoints Mới Được Trích Xuất Tự Động Từ Backend\n\n"
    for r in routes:
        generated_content += format_route_markdown(r)

    print(f"📝 Đang đối chiếu với tài liệu {api_md_path}...")
    if api_md_path.exists():
        with open(api_md_path, "r", encoding="utf-8") as f:
            existing_content = f.read()

        # Check if endpoints already documented
        missing_routes = []
        for r in routes:
            if r["path"] not in existing_content and r["name"] not in existing_content:
                missing_routes.append(r)

        if missing_routes:
            print(f"⚡ Phát hiện {len(missing_routes)} endpoint mới chưa có trong {args.output}. Đang tiến hành bổ sung...")
            append_block = "\n\n## 5. Endpoints Tự Động Đồng Bộ Từ Backend Code\n\n"
            for r in missing_routes:
                append_block += format_route_markdown(r)
            
            with open(api_md_path, "a", encoding="utf-8") as f:
                f.write(append_block)
            print(f"🎉 Đã tự động cập nhật thêm {len(missing_routes)} endpoints vào {args.output} thành công!")
        else:
            print(f"✨ Toàn bộ {len(routes)} endpoints đã có trong tài liệu {args.output}. Hợp đồng hoàn toàn đồng bộ!")
    else:
        with open(api_md_path, "w", encoding="utf-8") as f:
            f.write("# SAMS API Specification (Auto-generated)\n" + generated_content)
        print(f"🎉 Đã tạo mới tài liệu {args.output} thành công!")

if __name__ == "__main__":
    main()
