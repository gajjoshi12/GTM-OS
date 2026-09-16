from rest_framework import serializers

from .models import ActivityEvent, Agent, AgentRun, Command, Decision


class AgentSerializer(serializers.ModelSerializer):
    group_label = serializers.SerializerMethodField()

    class Meta:
        model = Agent
        fields = ("id", "key", "name", "group", "group_label", "description", "judged_on", "status", "enabled",
                  "runs_count", "success_rate", "health_score", "last_run_at", "last_summary", "config")
        read_only_fields = ("key", "name", "group", "runs_count", "success_rate", "health_score", "last_run_at", "last_summary")

    def get_group_label(self, obj):
        from .registry import GROUPS
        return GROUPS.get(obj.group, obj.group)


class AgentRunSerializer(serializers.ModelSerializer):
    agent_name = serializers.CharField(source="agent.name", read_only=True)
    agent_key = serializers.CharField(source="agent.key", read_only=True)

    class Meta:
        model = AgentRun
        fields = ("id", "agent", "agent_name", "agent_key", "trigger", "status", "mode", "input", "output", "summary",
                  "log", "tokens_used", "started_at", "finished_at", "duration_ms", "created_at")


class DecisionSerializer(serializers.ModelSerializer):
    agent_name = serializers.CharField(source="agent.name", read_only=True, default="AI CMO")
    agent_key = serializers.CharField(source="agent.key", read_only=True, default="cmo")

    class Meta:
        model = Decision
        fields = ("id", "agent", "agent_name", "agent_key", "title", "body", "category", "impact", "confidence", "status",
                  "requires_approval", "action", "metrics", "conversation", "resolved_at", "created_at")


class CommandSerializer(serializers.ModelSerializer):
    runs = AgentRunSerializer(many=True, read_only=True)

    class Meta:
        model = Command
        fields = ("id", "text", "status", "intent", "plan", "response", "runs", "created_at")


class ActivityEventSerializer(serializers.ModelSerializer):
    agent_name = serializers.CharField(source="agent.name", read_only=True, default="System")
    agent_key = serializers.CharField(source="agent.key", read_only=True, default="system")

    class Meta:
        model = ActivityEvent
        fields = ("id", "agent", "agent_name", "agent_key", "kind", "message", "meta", "created_at")
