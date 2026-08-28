from app.integrations.huggingface.gateway import ModelGateway,ModelRequest
class FakeProvider:
    def text_generation(self,model,prompt,max_new_tokens=128): return f"{model}:{prompt}:{max_new_tokens}"
def test_gateway_is_provider_agnostic():
    gateway=ModelGateway(); gateway.register("fake",FakeProvider())
    assert gateway.generate("fake",ModelRequest("m","hello",7))=="m:hello:7"
