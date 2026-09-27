import importlib.util
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).parents[1] / "app" / "utils" / "case_contract.py"
SPEC = importlib.util.spec_from_file_location("case_contract", MODULE_PATH)
CASE_CONTRACT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CASE_CONTRACT)


class CaseContractTests(unittest.TestCase):
    def test_legacy_case_service_fields_are_preserved_and_normalized(self):
        raw = {
            "success": True,
            "analysis": {"rama": "laboral"},
            "analysis_summary": {"tipo_proceso": "despido"},
            "strategy": {"claim_strategy": "Solicitar reposición"},
            "research": {"documents_found": 2},
            "legal_arguments": {"principal": "Tutela laboral"},
            "evidence_analysis": {"summary": "Contrato"},
            "risk_analysis": {"risks": ["Plazo"]},
            "counter_arguments": {"legal": ["Excepción"]},
            "timeline": [],
            "report": "# Informe",
        }

        normalized = CASE_CONTRACT.normalize_case_result(raw)

        self.assertEqual(normalized["summary"], raw["analysis_summary"])
        self.assertEqual(normalized["strategy"], raw["strategy"])
        self.assertEqual(normalized["risks"], raw["risk_analysis"])
        self.assertEqual(normalized["arguments"], raw["legal_arguments"])
        self.assertEqual(normalized["evidence"], raw["evidence_analysis"])
        self.assertEqual(normalized["report"], "# Informe")
        self.assertEqual(normalized["metadata"]["contract_version"], "1.0")

    def test_non_success_response_is_not_rewritten(self):
        failure = {"success": False, "error": "No disponible"}
        self.assertEqual(CASE_CONTRACT.normalize_case_result(failure), failure)


if __name__ == "__main__":
    unittest.main()
