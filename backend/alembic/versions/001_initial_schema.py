"""Initial database schema migration

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-10-21 19:30:00

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('username', sa.String(50), nullable=False, unique=True),
        sa.Column('email', sa.String(100), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(100), nullable=True),
        sa.Column('role', sa.String(20), default='analyst'),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True)
    )

    # Datasets table
    op.create_table(
        'datasets',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('name', sa.String(100), nullable=False, unique=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('adapter_type', sa.String(50), nullable=False),
        sa.Column('file_path', sa.String(255), nullable=False),
        sa.Column('file_size_bytes', sa.Integer(), default=0),
        sa.Column('total_rows', sa.Integer(), default=0),
        sa.Column('total_columns', sa.Integer(), default=0),
        sa.Column('benign_count', sa.Integer(), default=0),
        sa.Column('malicious_count', sa.Integer(), default=0),
        sa.Column('column_info', sa.JSON(), nullable=True),
        sa.Column('class_distribution', sa.JSON(), nullable=True),
        sa.Column('is_validated', sa.Boolean(), default=False),
        sa.Column('is_sample', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True)
    )

    # ML Models table
    op.create_table(
        'ml_models',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('name', sa.String(100), nullable=False, unique=True),
        sa.Column('version', sa.String(50), nullable=False),
        sa.Column('model_type', sa.String(50), default='FlowTransformer'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('dataset_id', sa.Integer(), sa.ForeignKey('datasets.id'), nullable=True),
        sa.Column('architecture_config', sa.JSON(), nullable=True),
        sa.Column('weights_path', sa.String(255), nullable=True),
        sa.Column('preprocessor_path', sa.String(255), nullable=True),
        sa.Column('target_classes', sa.JSON(), nullable=True),
        sa.Column('binary_threshold', sa.Float(), default=0.5),
        sa.Column('status', sa.String(30), default='untrained'),
        sa.Column('is_active', sa.Boolean(), default=False),
        sa.Column('accuracy', sa.Float(), nullable=True),
        sa.Column('precision', sa.Float(), nullable=True),
        sa.Column('recall', sa.Float(), nullable=True),
        sa.Column('f1_score', sa.Float(), nullable=True),
        sa.Column('roc_auc', sa.Float(), nullable=True),
        sa.Column('per_class_metrics', sa.JSON(), nullable=True),
        sa.Column('confusion_matrix', sa.JSON(), nullable=True),
        sa.Column('training_history', sa.JSON(), nullable=True),
        sa.Column('baseline_metrics', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True)
    )

    # Predictions table
    op.create_table(
        'predictions',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('flow_id', sa.String(100), nullable=False, unique=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.Column('src_ip', sa.String(50), nullable=True),
        sa.Column('dst_ip', sa.String(50), nullable=True),
        sa.Column('src_port', sa.Integer(), nullable=True),
        sa.Column('dst_port', sa.Integer(), nullable=True),
        sa.Column('protocol', sa.String(20), nullable=True),
        sa.Column('flow_features', sa.JSON(), nullable=True),
        sa.Column('model_id', sa.Integer(), sa.ForeignKey('ml_models.id'), nullable=True),
        sa.Column('model_version', sa.String(50), nullable=True),
        sa.Column('is_malicious', sa.Boolean(), nullable=False),
        sa.Column('predicted_class', sa.String(50), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('class_probabilities', sa.JSON(), nullable=True),
        sa.Column('inference_time_ms', sa.Float(), default=0.0),
        sa.Column('risk_score', sa.Float(), default=0.0),
        sa.Column('severity', sa.String(20), default='Low'),
        sa.Column('feature_importances', sa.JSON(), nullable=True),
        sa.Column('human_explanation', sa.Text(), nullable=True),
        sa.Column('model_evidence', sa.JSON(), nullable=True),
        sa.Column('llm_interpretation', sa.Text(), nullable=True),
        sa.Column('alert_created', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), nullable=True)
    )

    # Incidents table
    op.create_table(
        'incidents',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('incident_code', sa.String(50), nullable=False, unique=True),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('severity', sa.String(20), default='Medium'),
        sa.Column('status', sa.String(30), default='Open'),
        sa.Column('lead_analyst', sa.String(100), nullable=True),
        sa.Column('affected_assets', sa.JSON(), nullable=True),
        sa.Column('associated_iocs', sa.JSON(), nullable=True),
        sa.Column('mitre_tactics', sa.JSON(), nullable=True),
        sa.Column('mitre_techniques', sa.JSON(), nullable=True),
        sa.Column('root_cause', sa.Text(), nullable=True),
        sa.Column('mitigation_steps', sa.Text(), nullable=True),
        sa.Column('timeline', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True)
    )

    # Alerts table
    op.create_table(
        'alerts',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('alert_code', sa.String(50), nullable=False, unique=True),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('severity', sa.String(20), default='Medium'),
        sa.Column('risk_score', sa.Float(), default=50.0),
        sa.Column('confidence', sa.Float(), default=0.85),
        sa.Column('src_ip', sa.String(50), nullable=True),
        sa.Column('dst_ip', sa.String(50), nullable=True),
        sa.Column('src_port', sa.Integer(), nullable=True),
        sa.Column('dst_port', sa.Integer(), nullable=True),
        sa.Column('protocol', sa.String(20), nullable=True),
        sa.Column('prediction_id', sa.Integer(), sa.ForeignKey('predictions.id'), nullable=True),
        sa.Column('incident_id', sa.Integer(), sa.ForeignKey('incidents.id'), nullable=True),
        sa.Column('mitre_technique_id', sa.String(20), nullable=True),
        sa.Column('status', sa.String(30), default='New'),
        sa.Column('assigned_to', sa.String(100), nullable=True),
        sa.Column('resolution_notes', sa.Text(), nullable=True),
        sa.Column('evidence', sa.JSON(), nullable=True),
        sa.Column('investigation_notes', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True)
    )

    # IOCs table
    op.create_table(
        'iocs',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('value', sa.String(255), nullable=False, unique=True),
        sa.Column('ioc_type', sa.String(50), nullable=False),
        sa.Column('observed_status', sa.String(50), default='observed'),
        sa.Column('enrichment_status', sa.String(50), default='pending'),
        sa.Column('verification_status', sa.String(50), default='unverified'),
        sa.Column('severity', sa.String(20), default='Medium'),
        sa.Column('confidence_score', sa.Float(), default=0.5),
        sa.Column('threat_types', sa.JSON(), nullable=True),
        sa.Column('source', sa.String(100), default='Flow Inspection Engine'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('enrichment_data', sa.JSON(), nullable=True),
        sa.Column('reputation_score', sa.Integer(), nullable=True),
        sa.Column('last_enriched_at', sa.DateTime(), nullable=True),
        sa.Column('first_seen', sa.DateTime(), nullable=True),
        sa.Column('last_seen', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('related_alert_count', sa.Integer(), default=0),
        sa.Column('related_incident_count', sa.Integer(), default=0),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True)
    )

    # Threat relationships table
    op.create_table(
        'threat_relationships',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('source_ref', sa.String(100), nullable=False),
        sa.Column('source_type', sa.String(50), nullable=False),
        sa.Column('relationship_type', sa.String(50), nullable=False),
        sa.Column('target_ref', sa.String(100), nullable=False),
        sa.Column('target_type', sa.String(50), nullable=False),
        sa.Column('confidence', sa.Float(), default=0.7),
        sa.Column('rationale', sa.Text(), nullable=True),
        sa.Column('evidence', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True)
    )

    # MITRE techniques table
    op.create_table(
        'mitre_techniques',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('technique_id', sa.String(50), nullable=False, unique=True),
        sa.Column('name', sa.String(150), nullable=False),
        sa.Column('tactic', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('attack_categories', sa.JSON(), nullable=True),
        sa.Column('mapping_rationale', sa.Text(), nullable=True),
        sa.Column('detection_rule_summary', sa.Text(), nullable=True),
        sa.Column('attck_version', sa.String(20), default='v14.1'),
        sa.Column('confidence_weight', sa.Float(), default=0.85),
        sa.Column('url', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True)
    )

    # Federated Clients table
    op.create_table(
        'federated_clients',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('client_id', sa.String(50), nullable=False, unique=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('organization', sa.String(100), nullable=False),
        sa.Column('industry_sector', sa.String(50), default='Finance'),
        sa.Column('dataset_name', sa.String(100), nullable=False),
        sa.Column('local_sample_count', sa.Integer(), default=1000),
        sa.Column('status', sa.String(30), default='active'),
        sa.Column('current_round', sa.Integer(), default=0),
        sa.Column('local_accuracy', sa.Float(), nullable=True),
        sa.Column('local_loss', sa.Float(), nullable=True),
        sa.Column('last_heartbeat', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True)
    )

    # Federated Rounds table
    op.create_table(
        'federated_rounds',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('round_number', sa.Integer(), nullable=False, unique=True),
        sa.Column('status', sa.String(30), default='completed'),
        sa.Column('aggregation_strategy', sa.String(50), default='FedAvg'),
        sa.Column('participating_clients', sa.JSON(), nullable=True),
        sa.Column('total_samples', sa.Integer(), default=0),
        sa.Column('global_accuracy_before', sa.Float(), nullable=True),
        sa.Column('global_accuracy_after', sa.Float(), nullable=True),
        sa.Column('global_loss_before', sa.Float(), nullable=True),
        sa.Column('global_loss_after', sa.Float(), nullable=True),
        sa.Column('client_metrics', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True)
    )

    # Audit Events table
    op.create_table(
        'audit_events',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.Column('username', sa.String(50), default='system'),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('resource_type', sa.String(50), nullable=False),
        sa.Column('resource_id', sa.String(100), nullable=True),
        sa.Column('status', sa.String(20), default='success'),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('ip_address', sa.String(50), nullable=True)
    )

    # System Settings table
    op.create_table(
        'system_settings',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('key', sa.String(100), nullable=False, unique=True),
        sa.Column('value', sa.Text(), nullable=False),
        sa.Column('description', sa.String(255), nullable=True),
        sa.Column('is_secret', sa.Boolean(), default=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True)
    )

def downgrade() -> None:
    op.drop_table('system_settings')
    op.drop_table('audit_events')
    op.drop_table('federated_rounds')
    op.drop_table('federated_clients')
    op.drop_table('mitre_techniques')
    op.drop_table('threat_relationships')
    op.drop_table('iocs')
    op.drop_table('alerts')
    op.drop_table('incidents')
    op.drop_table('predictions')
    op.drop_table('ml_models')
    op.drop_table('datasets')
    op.drop_table('users')
