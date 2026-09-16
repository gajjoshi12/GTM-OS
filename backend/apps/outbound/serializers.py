from rest_framework import serializers

from .models import Enrollment, OutboundMessage, Reply, Sequence


class SequenceSerializer(serializers.ModelSerializer):
    reply_rate = serializers.FloatField(read_only=True)
    icp_name = serializers.CharField(source="icp.name", read_only=True, default="")

    class Meta:
        model = Sequence
        exclude = ("workspace",)


class EnrollmentSerializer(serializers.ModelSerializer):
    contact_name = serializers.CharField(source="contact.full_name", read_only=True)
    company_name = serializers.CharField(source="contact.company.name", read_only=True)

    class Meta:
        model = Enrollment
        exclude = ("workspace",)


class OutboundMessageSerializer(serializers.ModelSerializer):
    contact_name = serializers.CharField(source="contact.full_name", read_only=True)
    company_name = serializers.CharField(source="contact.company.name", read_only=True)

    class Meta:
        model = OutboundMessage
        exclude = ("workspace",)


class ReplySerializer(serializers.ModelSerializer):
    contact_name = serializers.CharField(source="contact.full_name", read_only=True)
    contact_title = serializers.CharField(source="contact.title", read_only=True)
    company_name = serializers.CharField(source="contact.company.name", read_only=True)
    company_tier = serializers.IntegerField(source="contact.company.tier", read_only=True)
    sequence_name = serializers.CharField(source="sequence.name", read_only=True, default="")

    class Meta:
        model = Reply
        exclude = ("workspace",)
