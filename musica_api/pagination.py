"""
Modelos de paginación para la API de Música.
Proporciona estructuras para manejar respuestas paginadas.
Desarrollado por Isabella Ramírez Franco (@codebell-alt)
"""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

# Tipo genérico para los elementos de la página
T = TypeVar("T")


class PaginationParams(BaseModel):
    """
    Parámetros de paginación para las consultas.
    """

    page: int = Field(default=1, ge=1, description="Número de página (mínimo 1)")
    size: int = Field(
        default=10, ge=1, le=100, description="Elementos por página (1-100)"
    )

    @property
    def offset(self) -> int:
        """Calcula el offset para la consulta SQL."""
        return (self.page - 1) * self.size

    @property
    def limit(self) -> int:
        """Retorna el límite para la consulta SQL."""
        return self.size


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Respuesta paginada genérica que puede contener cualquier tipo de datos.
    """

    items: list[T] = Field(description="Elementos de la página actual")
    total: int = Field(description="Número total de elementos")
    page: int = Field(description="Página actual")
    size: int = Field(description="Elementos por página")
    pages: int = Field(description="Número total de páginas")

    @classmethod
    def create(
        cls,
        items: list[T],
        total: int,
        page: int,
        size: int,
    ) -> "PaginatedResponse[T]":
        """
        Factory method para crear una respuesta paginada.

        Args:
            items: Lista de elementos para la página actual
            total: Número total de elementos
            page: Número de página actual
            size: Elementos por página

        Returns:
            PaginatedResponse con los datos paginados
        """
        pages = (total + size - 1) // size  # Ceiling division
        return cls(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=pages,
        )


class PaginationMeta(BaseModel):
    """
    Metadatos de paginación para incluir en las respuestas.
    """

    page: int = Field(description="Página actual")
    size: int = Field(description="Elementos por página")
    total: int = Field(description="Total de elementos")
    pages: int = Field(description="Total de páginas")
    has_next: bool = Field(description="Indica si hay página siguiente")
    has_prev: bool = Field(description="Indica si hay página anterior")
    next_page: int | None = Field(description="Número de página siguiente")
    prev_page: int | None = Field(description="Número de página anterior")

    @classmethod
    def create(cls, page: int, size: int, total: int) -> "PaginationMeta":
        """
        Factory method para crear metadatos de paginación.

        Args:
            page: Número de página actual
            size: Elementos por página
            total: Número total de elementos

        Returns:
            PaginationMeta con los metadatos calculados
        """
        pages = (total + size - 1) // size
        has_next = page < pages
        has_prev = page > 1

        return cls(
            page=page,
            size=size,
            total=total,
            pages=pages,
            has_next=has_next,
            has_prev=has_prev,
            next_page=page + 1 if has_next else None,
            prev_page=page - 1 if has_prev else None,
        )
