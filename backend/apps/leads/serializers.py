from rest_framework import serializers

from .models import ICP, Company, Contact


class ICPSerializer(serializers.ModelSerializer):
    class Meta:
        model = ICP
        exclude = ("workspace",)


class ContactSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    company_name = serializers.CharField(source="company.name", read_only=True)
    company_tier = serializers.IntegerField(source="company.tier", read_only=True)
    company_fit_score = serializers.IntegerField(source="company.fit_score", read_only=True)

    class Meta:
        model = Contact
        exclude = ("workspace",)


class CompanySerializer(serializers.ModelSerializer):
    icp_name = serializers.CharField(source="icp.name", read_only=True, default="")
    contacts_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Company
        exclude = ("workspace",)


class CompanyDetailSerializer(CompanySerializer):
    contacts = ContactSerializer(many=True, read_only=True)
