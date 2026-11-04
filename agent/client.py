# -*- coding: utf-8 -*-
"""IOT Solar AutoTest HTTP 客户端（出站 HTTPS/HTTP）。

报文标识字段与《WebSocket 数据通信原则》一致：
pythonid / clientid / experid / type / status / equs / commands / rep_url
"""
from __future__ import annotations

import json
from typing import Any, Dict, Optional

from agent.http_tls import http_exchange


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
        status, raw_b = http_exchange(
            method, url, data=data, headers=headers, timeout=self.timeout
        )
        raw = raw_b.decode("utf-8", errors="replace")
        if status >= 400:
            raise RuntimeError(f"HTTP {status} {path}: {raw[:400]}")
        return json.loads(raw) if raw else {}

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
        error_logs: Optional[list] = None,
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
        if error_logs:
            body["errorLogs"] = list(error_logs)
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
        # 协议 startexper：id=solar_jobs 主键；experid 可为 experiments.id
        from agent.job_normalize import normalize_startexper_job

        data = normalize_startexper_job(data if isinstance(data, dict) else {})
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
        self,
        *,
        test_type: str,
        title: str = "",
        widgets: Optional[dict] = None,
        run_commands: Optional[list] = None,
        blockly_code: str = "",
        blockly_xml: str = "",
    ) -> Dict[str, Any]:
        """台架本地点开始：向 IOT 登记实验 + RUNNING 任务。

        widgets / runCommands / blockly* 应为本机实际工况与步骤，一并落库。
        """
        body: Dict[str, Any] = {
            "type": "local_run_start",
            "pythonid": self.pythonid,
            "clientid": self.clientid,
            "testType": (test_type or "").strip() or "overload",
            "title": (title or "").strip(),
        }
        if isinstance(widgets, dict) and widgets:
            body["widgets"] = widgets
        if isinstance(run_commands, list) and run_commands:
            body["runCommands"] = run_commands
        if (blockly_code or "").strip():
            body["blocklyCode"] = blockly_code.strip()
        if (blockly_xml or "").strip():
            body["blocklyXml"] = blockly_xml.strip()
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

    def sync_dc1_widgets(self, widgets: Dict[str, Any]) -> Dict[str, Any]:
        """蓝点曲线换算的直流四点，写进本台架进行中实验和记住的参数。"""
        return self._request(
            "POST",
            "/api/solar-autotest/agent/local-run/dc-iv",
            {"widgets": dict(widgets or {})},
        )

    def seed_curve_points(
        self,
        job_id: int,
        points: list,
        *,
        replace: bool = False,
    ) -> Dict[str, Any]:
        """回填 U/I/P 采点（模拟工况或结案后补曲线）。"""
        return self._request(
            "POST",
            f"/api/solar-autotest/agent/jobs/{int(job_id)}/curve-points",
            {"points": points or [], "replace": bool(replace)},
        )

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
        status, raw_b = http_exchange(
            "POST",
            url,
            data=body,
            headers={
                "X-Solar-Agent-Token": self.token,
                "Content-Type": f"multipart/form-data; boundary={boundary}",
                "Accept": "application/json",
            },
            timeout=self.timeout,
        )
        raw = raw_b.decode("utf-8", errors="replace")
        if status >= 400:
            raise RuntimeError(f"HTTP {status} upload_report: {raw[:400]}")
        return json.loads(raw or "{}")
