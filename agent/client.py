# -*- coding: utf-8 -*-
"""IOT Solar AutoTest HTTP 客户端（出站 HTTPS/HTTP）。

报文标识字段与《WebSocket 数据通信原则》一致：
pythonid / clientid / experid / type / status / equs / commands / rep_url
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any, Dict, Optional


class IotSolarClient:
    def __init__(self, base: str, token: str, timeout: float = 30.0, pythonid: str = ""):
        self.base = base.rstrip("/")
        self.token = token
        self.timeout = timeout
        self.pythonid = pythonid or ""
        self.clientid = ""

    def _request(self, method: str, path: str, body: Optional[dict] = None) -> Dict[str, Any]:
        url = f"{self.base}{path}"
        data = None
        headers = {
            "X-Solar-Agent-Token": self.token,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if body is not None:
            data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"HTTP {e.code} {path}: {detail}") from e

    def heartbeat(
        self,
        *,
        agent_version: str = "",
        host_name: str = "",
        busy: bool = False,
        fault: bool = False,
        instruments: Optional[list] = None,
        probe_results: Optional[list] = None,
        probe_request_id: str = "",
        control_result: Optional[dict] = None,
        control_request_id: str = "",
        local_resources: Optional[list] = None,
        run_snapshot: Optional[dict] = None,
    ) -> Dict[str, Any]:
        body: Dict[str, Any] = {
            "type": "on",
            "pythonid": self.pythonid,
            "clientid": self.clientid,
            "agent_version": agent_version,
            "host_name": host_name,
            "busy": busy,
            "fault": fault,
        }
        if instruments is not None:
            body["instruments"] = list(instruments)
        if probe_results is not None:
            body["probeResults"] = list(probe_results)
            if probe_request_id:
                body["probeRequestId"] = str(probe_request_id)
        if control_result is not None:
            body["controlResult"] = dict(control_result)
            if control_request_id:
                body["controlRequestId"] = str(control_request_id)
        if local_resources is not None:
            body["localResources"] = list(local_resources)
        if run_snapshot is not None:
            body["runSnapshot"] = dict(run_snapshot)
        return self._request(
            "POST",
            "/api/solar-autotest/agent/heartbeat",
            body,
        )

    def claim_next(self) -> Optional[Dict[str, Any]]:
        res = self._request("GET", "/api/solar-autotest/agent/jobs/next")
        data = res.get("data")
        if not data:
            return None
        # 协议 startexper：id=solar_jobs 主键（HTTPS）；experid 可为实验 id
        if "id" not in data and "experid" in data:
            try:
                data = dict(data)
                data["id"] = int(data["experid"])
            except (TypeError, ValueError):
                pass
        # commands.command 内嵌 JSON 时可还原 params
        cmds = data.get("commands") if isinstance(data, dict) else None
        if isinstance(cmds, dict) and not data.get("params"):
            raw = cmds.get("command")
            if isinstance(raw, str) and raw.strip().startswith("{"):
                try:
                    nested = json.loads(raw)
                    if isinstance(nested, dict):
                        data.setdefault("testType", nested.get("testType") or "")
                        data.setdefault("title", nested.get("title") or "")
                        data.setdefault("params", nested.get("params") or {})
                except json.JSONDecodeError:
                    pass
        if self.pythonid == "" and isinstance(data, dict):
            self.pythonid = str(data.get("pythonid") or "")
        return data

    def get_job(self, job_id: int) -> dict:
        """查询本台架任务状态（远程中止轮询）。"""
        res = self._request("GET", f"/api/solar-autotest/agent/jobs/{int(job_id)}")
        data = res.get("data")
        if not isinstance(data, dict):
            return {}
        return data

    def progress(
        self,
        job_id: int,
        *,
        progress_percent: Optional[int] = None,
        progress_text: str = "",
        current_step: str = "",
        measures: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        pct = 0 if progress_percent is None else int(progress_percent)
        equ: Dict[str, Any] = {
            "equ_id": f"SOLAR-JOB-{job_id}",
            "progress_percent": pct,
            "progress_text": progress_text,
            "current_step": current_step,
        }
        if isinstance(measures, dict) and measures:
            equ["measures"] = dict(measures)
        body: Dict[str, Any] = {
            "type": "experdata",
            "pythonid": self.pythonid,
            "clientid": self.clientid,
            "experid": str(job_id),
            "time": "1",
            "equs": [equ],
        }
        if isinstance(measures, dict) and measures:
            body["measures"] = dict(measures)
        return self._request("POST", f"/api/solar-autotest/agent/jobs/{job_id}/progress", body)

    def done(
        self,
        job_id: int,
        *,
        status: str,
        fail_reason: str = "",
        result_summary: Optional[dict] = None,
        report_meta: Optional[list] = None,
    ) -> Dict[str, Any]:
        # 协议返回 status：OK / NG / FAIL；同时带业务 status 映射由服务端处理
        proto_status = {
            "success": "OK",
            "aborted": "NG",
            "failed": "FAIL",
            "ok": "OK",
            "ng": "NG",
            "fail": "FAIL",
        }.get(str(status or "").lower(), status)
        body: Dict[str, Any] = {
            "type": "exper_auto_end",
            "pythonid": self.pythonid,
            "clientid": self.clientid,
            "experid": str(job_id),
            "status": proto_status,
            "fail_reason": fail_reason,
            "result_summary": result_summary or {},
        }
        if report_meta:
            body["report_meta"] = report_meta
        return self._request(
            "POST",
            f"/api/solar-autotest/agent/jobs/{job_id}/done",
            body,
        )

    def local_run_start(
        self, *, test_type: str, title: str = "", widgets: Optional[dict] = None
    ) -> Dict[str, Any]:
        """台架本地点开始：向 IOT 登记实验 + RUNNING 任务。"""
        body: Dict[str, Any] = {
            "type": "local_run_start",
            "pythonid": self.pythonid,
            "clientid": self.clientid,
            "testType": (test_type or "").strip() or "overload",
            "title": (title or "").strip(),
        }
        if isinstance(widgets, dict) and widgets:
            body["widgets"] = widgets
        res = self._request("POST", "/api/solar-autotest/agent/local-run/start", body)
        data = res.get("data") if isinstance(res, dict) else None
        return data if isinstance(data, dict) else (res if isinstance(res, dict) else {})

    def reject(self, job_id: int, reason: str) -> Dict[str, Any]:
        return self._request(
            "POST",
            f"/api/solar-autotest/agent/jobs/{job_id}/reject",
            {
                "type": "endexper_return",
                "pythonid": self.pythonid,
                "clientid": self.clientid,
                "experid": str(job_id),
                "status": "NG",
                "reason": reason,
            },
        )

    def get_prefs(self) -> Dict[str, Any]:
        return self._request("GET", "/api/solar-autotest/agent/prefs")

    def put_prefs(self, body: dict) -> Dict[str, Any]:
        return self._request("PUT", "/api/solar-autotest/agent/prefs", body or {})

    def upload_report(self, job_id: int, file_path: str, filename: Optional[str] = None) -> Dict[str, Any]:
        """multipart 上传报告文件到 IOT。"""
        import mimetypes
        from pathlib import Path

        path = Path(file_path)
        name = filename or path.name
        boundary = "----SolarAgentBoundary7MA4YWxk"
        raw = path.read_bytes()
        ctype = mimetypes.guess_type(name)[0] or "application/octet-stream"
        body = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="file"; filename="{name}"\r\n'
            f"Content-Type: {ctype}\r\n\r\n"
        ).encode("utf-8") + raw + f"\r\n--{boundary}--\r\n".encode("utf-8")
        url = f"{self.base}/api/solar-autotest/agent/jobs/{job_id}/report"
        req = urllib.request.Request(
            url,
            data=body,
            headers={
                "X-Solar-Agent-Token": self.token,
                "Content-Type": f"multipart/form-data; boundary={boundary}",
                "Accept": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode("utf-8") or "{}")
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"HTTP {e.code} upload_report: {detail}") from e
