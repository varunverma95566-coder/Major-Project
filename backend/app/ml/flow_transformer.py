"""FlowTransformer: PyTorch Transformer Encoder for Flow-Based NIDS.

Implements feature token projection, positional/feature embeddings,
multi-head self-attention encoder layers, and dual binary/multiclass classification heads.
Inspired by FlowTransformer research foundations.
"""

import math
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Any, Tuple, Optional


class FeatureTokenizer(nn.Module):
    """Projects numerical features and embeds categorical features into a shared embedding space."""
    def __init__(self, num_numerical: int, cat_cardinalities: list, embedding_dim: int):
        super().__init__()
        self.num_numerical = num_numerical
        self.embedding_dim = embedding_dim
        
        # Linear projection for each numerical feature
        # Weight shape: (num_numerical, embedding_dim), bias: (num_numerical, embedding_dim)
        self.num_weights = nn.Parameter(torch.Tensor(num_numerical, embedding_dim))
        self.num_biases = nn.Parameter(torch.Tensor(num_numerical, embedding_dim))
        nn.init.kaiming_uniform_(self.num_weights, a=math.sqrt(5))
        nn.init.zeros_(self.num_biases)
        
        # Categorical feature embeddings
        self.cat_embeddings = nn.ModuleList([
            nn.Embedding(cardinality + 2, embedding_dim) for cardinality in cat_cardinalities
        ])
        
        # Feature identifier embeddings (acts like positional encoding for tabular features)
        total_tokens = num_numerical + len(cat_cardinalities) + 1  # +1 for CLS token
        self.feature_embeddings = nn.Embedding(total_tokens, embedding_dim)
        
        # Learnable CLS token
        self.cls_token = nn.Parameter(torch.zeros(1, 1, embedding_dim))
        nn.init.normal_(self.cls_token, std=0.02)

    def forward(self, x_num: torch.Tensor, x_cat: torch.Tensor) -> torch.Tensor:
        batch_size = x_num.size(0)
        
        # Numerical feature projection: (batch_size, num_num, 1) * (1, num_num, emb_dim)
        x_num_expanded = x_num.unsqueeze(-1)
        tokens_num = x_num_expanded * self.num_weights.unsqueeze(0) + self.num_biases.unsqueeze(0)
        
        # Categorical tokens
        tokens_cat_list = []
        if x_cat.size(1) > 0:
            for i, emb_layer in enumerate(self.cat_embeddings):
                tokens_cat_list.append(emb_layer(x_cat[:, i]).unsqueeze(1))
            tokens_cat = torch.cat(tokens_cat_list, dim=1)
            tokens = torch.cat([tokens_num, tokens_cat], dim=1)
        else:
            tokens = tokens_num

        # Prepend [CLS] token
        cls_tokens = self.cls_token.expand(batch_size, -1, -1)
        tokens = torch.cat([cls_tokens, tokens], dim=1)
        
        # Add feature identifier embeddings
        seq_len = tokens.size(1)
        feature_ids = torch.arange(seq_len, device=tokens.device).unsqueeze(0).expand(batch_size, -1)
        tokens = tokens + self.feature_embeddings(feature_ids)
        
        return tokens


class FlowTransformer(nn.Module):
    def __init__(
        self,
        num_numerical: int,
        cat_cardinalities: list,
        num_classes: int,
        embedding_dim: int = 64,
        num_heads: int = 4,
        num_layers: int = 2,
        feedforward_dim: int = 128,
        dropout: float = 0.1
    ):
        super().__init__()
        assert embedding_dim % num_heads == 0, f"embedding_dim ({embedding_dim}) must be divisible by num_heads ({num_heads})"
        
        self.embedding_dim = embedding_dim
        self.num_classes = num_classes
        
        # Feature Tokenizer
        self.tokenizer = FeatureTokenizer(num_numerical, cat_cardinalities, embedding_dim)
        
        # Transformer Encoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embedding_dim,
            nhead=num_heads,
            dim_feedforward=feedforward_dim,
            dropout=dropout,
            activation="relu",
            batch_first=True
        )
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        
        self.layer_norm = nn.LayerNorm(embedding_dim)
        
        # Dual Classification Heads
        # 1. Binary head (Benign vs Malicious)
        self.binary_head = nn.Sequential(
            nn.Linear(embedding_dim, 32),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(32, 1)
        )
        
        # 2. Multiclass head (Specific attack classification)
        self.multiclass_head = nn.Sequential(
            nn.Linear(embedding_dim, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, num_classes)
        )

    def forward(self, x_num: torch.Tensor, x_cat: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Returns:
            binary_logits: (batch_size, 1)
            multiclass_logits: (batch_size, num_classes)
        """
        tokens = self.tokenizer(x_num, x_cat)
        encoded = self.transformer_encoder(tokens)
        
        # Extract [CLS] representation (index 0)
        cls_rep = self.layer_norm(encoded[:, 0, :])
        
        binary_logits = self.binary_head(cls_rep).squeeze(-1)
        multiclass_logits = self.multiclass_head(cls_rep)
        
        return binary_logits, multiclass_logits

    def predict_proba(self, x_num: torch.Tensor, x_cat: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        self.eval()
        with torch.no_grad():
            binary_logits, multiclass_logits = self.forward(x_num, x_cat)
            binary_probs = torch.sigmoid(binary_logits)
            multiclass_probs = F.softmax(multiclass_logits, dim=-1)
        return binary_probs, multiclass_probs
