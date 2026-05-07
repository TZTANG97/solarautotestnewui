"""
�������ԣ����Ӱ���Э��ת���� Modbus TCP�����Ϳ������

�÷�������Ŀ��Ŀ¼��:
    python test_itech_modbus_poweron.py

Ĭ��: 192.168.40.211:8080������ SYST:POWER ON���� ItechTranslator �С�������һ�£���
"""
from __future__ import annotations

import argparse
import logging
import sys

from pymodbus.client import ModbusTcpClient

from scpi_to_modbustcp import ItechTranslator

logger = logging.getLogger(__name__)


def main() -> int:
    parser = argparse.ArgumentParser(description="���� ItechTranslator Modbus ����")
    parser.add_argument("--host", default="192.168.40.211", help="Modbus TCP ����")
    parser.add_argument("--port", type=int, default=8080, help="Modbus TCP �˿�")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="���������ӣ���д��Ĵ�������д������",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    client = ModbusTcpClient(host=args.host, port=args.port, timeout=5, retries=3)
    if not client.connect():
        logger.error("Modbus ����ʧ��: %s:%s", args.host, args.port)
        return 1

    logger.info("Modbus ������: %s:%s", args.host, args.port)

    try:
        if args.dry_run:
            logger.info("dry-run������д�Ĵ������������������˳�")
            return 0

        translator = ItechTranslator(client)
        ok = translator.translate("SYST:POWER ON")
        if not ok:
            logger.error("translate(SYST:POWER ON) ���� False")
            return 1
        logger.info("�ѷ��Ϳ������� (SYST:POWER ON -> �Ĵ��� 0x0909, ֵ 0x0002)")
    except Exception as e:
        logger.exception("���Ϳ���ʧ��: %s", e)
        return 1
    finally:
        client.close()
        logger.info("�����ѹر�")

    return 0


if __name__ == "__main__":
    sys.exit(main())
