from types import SimpleNamespace
from app.integrations.huggingface.metadata import ModelCardSync
def test_metadata_normalization():
    m=ModelCardSync().normalize(SimpleNamespace(id="org/model",sha="abc",pipeline_tag="text-generation",library_name="transformers",tags=["x"]))
    assert m.repo_id=="org/model" and m.revision=="abc" and m.tags==("x",)
