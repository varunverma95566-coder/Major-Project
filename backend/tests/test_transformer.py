import torch
import pytest
from app.ml.flow_transformer import FlowTransformer

def test_flow_transformer_forward_and_shapes():
    batch_size = 8
    num_numerical = 20
    cat_cardinalities = [5, 4]
    num_classes = 4
    embedding_dim = 64
    num_heads = 4
    num_layers = 2

    model = FlowTransformer(
        num_numerical=num_numerical,
        cat_cardinalities=cat_cardinalities,
        num_classes=num_classes,
        embedding_dim=embedding_dim,
        num_heads=num_heads,
        num_layers=num_layers
    )

    x_num = torch.randn(batch_size, num_numerical)
    x_cat = torch.randint(0, 3, (batch_size, len(cat_cardinalities)))

    binary_logits, multiclass_logits = model(x_num, x_cat)

    assert binary_logits.shape == (batch_size,)
    assert multiclass_logits.shape == (batch_size, num_classes)

    # Test probability outputs
    b_probs, m_probs = model.predict_proba(x_num, x_cat)
    assert b_probs.shape == (batch_size,)
    assert m_probs.shape == (batch_size, num_classes)
    assert torch.all(b_probs >= 0.0) and torch.all(b_probs <= 1.0)
    assert torch.allclose(m_probs.sum(dim=-1), torch.ones(batch_size), atol=1e-5)
