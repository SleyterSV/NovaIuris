"""Synthetic Zep ontology probe. Run from backend with configured ZEP_API_KEY."""
import json
import os

from zep_cloud import BadRequestError

from app.services.graph_builder import GraphBuilderService, safe_zep_validation_details
from app.utils.novacourt_graph import ENTITY_TYPES, provider_ontology


def main():
    if not os.getenv("ZEP_API_KEY"):
        print("LIVE_ZEP=OPERATOR_REQUIRED")
        return 2
    builder = GraphBuilderService()
    graph_id = None
    try:
        ontology = provider_ontology([{"entity_type": kind} for kind in ENTITY_TYPES])
        graph_id = builder.create_graph("NovaCourt Ontology QA")
        builder.set_ontology(graph_id, ontology)
        print("ONTOLOGY_ACCEPTED")
        return 0
    except BadRequestError as error:
        print("ONTOLOGY_REJECTED " + json.dumps(safe_zep_validation_details(error), sort_keys=True))
        return 1
    except Exception as error:
        print("ONTOLOGY_PROBE_FAILED error_type=" + type(error).__name__
              + " http_status=" + str(getattr(error, "status_code", None)))
        return 1
    finally:
        if graph_id:
            try:
                builder.delete_graph(graph_id)
            except Exception:
                print("SYNTHETIC_GRAPH_CLEANUP_REQUIRED graph_id=" + graph_id)


if __name__ == "__main__":
    raise SystemExit(main())
