"""Workspace scoping helpers shared by every domain app."""
from __future__ import annotations

from django.db import models
from rest_framework.exceptions import PermissionDenied

from apps.accounts.models import Workspace


class WorkspaceModel(models.Model):
    """Abstract base: every tenant-owned row carries a workspace FK + timestamps."""

    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="%(class)ss")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ("-created_at",)


def get_workspace(request) -> Workspace:
    """Resolve the active workspace: `X-Workspace` header wins, else the user's current one."""
    user = request.user
    header = request.headers.get("X-Workspace")
    if header:
        ws = Workspace.objects.filter(id=header, memberships__user=user).first()
        if not ws:
            raise PermissionDenied("Not a member of that workspace.")
        return ws
    if user.current_workspace_id:
        return user.current_workspace
    membership = user.memberships.select_related("workspace").first()
    if not membership:
        raise PermissionDenied("No workspace available for this user.")
    return membership.workspace


class WorkspaceScopedMixin:
    """Mixin for ViewSets: filters by workspace and stamps it on create."""

    def get_workspace(self):
        if not hasattr(self, "_workspace"):
            self._workspace = get_workspace(self.request)
        return self._workspace

    def get_queryset(self):
        return super().get_queryset().filter(workspace=self.get_workspace())

    def perform_create(self, serializer):
        serializer.save(workspace=self.get_workspace())
