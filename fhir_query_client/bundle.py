import pandas as pd

from fhir_query_client import utils
from fhir_query_client.constants import DF_DEFAULT_COLUMNS


class FQCBundle:
    """
    A custom bundle to abstract the bundle response from the fhir server.
    """

    def __init__(self, bundle: dict):
        self.data = bundle

    @property
    def resource(self) -> dict | None:
        if self.size == 1:
            return self.resources[0]
        elif self.size > 1:
            raise ValueError("Bundle contains more than one resource")
        else:
            return None

    @property
    def resources(self) -> list[dict]:
        return utils.get_resources_from_bundle(self.data)

    @property
    def next_link(self) -> str | None:
        return utils.get_next_link(self.data)

    @property
    def previous_link(self) -> str | None:
        return utils.get_previous_link(self.data)

    @property
    def total(self) -> int | None:
        return self.data.get("total", None)

    @property
    def size(self) -> int:
        return len(self.resources)

    def to_df(self, columns: dict[str, str] | None = None) -> pd.DataFrame:
        """Convert the Bundle's resources to a pandas DataFrame.

        Args:
            columns (Optional[Dict[str, str]]): Dictionary mapping column names to FHIRPath
                expressions. If None, uses default columns for the resource type if available.

        Returns:
            pd.DataFrame: DataFrame where each row represents a resource and columns are
                specified by the FHIRPath expressions.

        Raises:
            ValueError: If Bundle is empty and no columns are specified, or if no default
                columns exist for the resource type.
        """

        if self.size == 0 and columns is None:
            raise ValueError("Bundle is empty and no columns specified")
        first_resource_type = self.resources[0]["resourceType"]
        if columns is None:
            if first_resource_type in DF_DEFAULT_COLUMNS:
                columns = DF_DEFAULT_COLUMNS[first_resource_type]
            else:
                raise ValueError(
                    f"No default columns for resource type: {first_resource_type}"
                )

        return utils.bundle_to_df(self.data, columns)

    def add_bundle(self, bundle: dict):
        self.data["entry"].extend(bundle.get("entry", []))

    def collect_resource_types(self) -> list[str]:
        return [resource["resourceType"] for resource in self.resources]

    def collect_resources_by_type(self, resource_type: str) -> list[dict]:
        return [
            resource
            for resource in self.resources
            if resource["resourceType"] == resource_type
        ]

    def collect_ids(self) -> list[str]:
        return [resource["id"] for resource in self.resources]

    def __len__(self) -> int:
        return len(self.resources)

    def __getitem__(self, index: int) -> dict:
        return self.resources[index]

    def __iter__(self):
        return iter(self.resources)

    def __contains__(self, item: dict) -> bool:
        return item in self.resources

    def __repr__(self) -> str:
        return f"FQCBundle(total={self.total}, size={self.size})"

    def __str__(self) -> str:
        return f"FQCBundle(total={self.total}, size={self.size})"

    def __bool__(self) -> bool:
        return bool(self.resources)
