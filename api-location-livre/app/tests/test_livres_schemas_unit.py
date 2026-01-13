import pytest
from pydantic import ValidationError

from app.routers.livres import LivreCreate, LivreUpdate


def test_livre_create_minimal_valid():
    payload = LivreCreate(
        titre="Titre",
        auteur="Auteur",
        annee=2024,
        nombre_copies=1,
    )
    assert payload.titre == "Titre"
    assert payload.auteur == "Auteur"
    assert payload.annee == 2024
    assert payload.nombre_copies == 1
    assert payload.copies_disponibles is None


def test_livre_create_with_alias_fields():
    data = {
        "titre": "Alias Titre",
        "auteur": "Alias Auteur",
        "annee": 2023,
        "nombreCopies": 5,
        "copiesDisponibles": 3,
    }
    payload = LivreCreate(**data)
    assert payload.titre == "Alias Titre"
    assert payload.auteur == "Alias Auteur"
    assert payload.annee == 2023
    assert payload.nombre_copies == 5
    assert payload.copies_disponibles == 3


def test_livre_create_nombre_copies_must_be_positive():
    """
    nombre_copies < 1 doit lever une ValidationError via le validator Pydantic.
    """
    with pytest.raises(ValidationError):
        LivreCreate(
            titre="Bad",
            auteur="Bad",
            annee=2024,
            nombre_copies=0,  # invalide
        )


def test_livre_create_nombre_copies_one_is_ok():
    payload = LivreCreate(
        titre="OK",
        auteur="OK",
        annee=2024,
        nombre_copies=1,
    )
    assert payload.nombre_copies == 1


def test_livre_update_all_fields_none_is_valid():
    payload = LivreUpdate()
    assert payload.titre is None
    assert payload.auteur is None
    assert payload.annee is None
    assert payload.nombre_copies is None
    assert payload.copies_disponibles is None


def test_livre_update_partial_update_titre_only():
    payload = LivreUpdate(titre="Nouveau titre")
    assert payload.titre == "Nouveau titre"
    assert payload.auteur is None
    assert payload.annee is None


def test_livre_update_with_aliases():
    data = {
        "titre": "Titre MAJ",
        "auteur": "Auteur MAJ",
        "annee": 2020,
        "nombreCopies": 10,
        "copiesDisponibles": 4,
    }
    payload = LivreUpdate(**data)
    assert payload.titre == "Titre MAJ"
    assert payload.auteur == "Auteur MAJ"
    assert payload.annee == 2020
    assert payload.nombre_copies == 10
    assert payload.copies_disponibles == 4


def test_livre_create_forbid_extra_fields():
    data = {
        "titre": "Titre",
        "auteur": "Auteur",
        "annee": 2024,
        "nombreCopies": 3,
        "champInconnu": "doit être rejeté",
    }
    try:
        LivreCreate(**data)
        # Si on arrive ici, c'est que le modèle n'a pas rejeté le champ inconnu
        assert False, "LivreCreate aurait dû rejeter les champs extra"
    except ValidationError as e:
        # On vérifie qu'il y a bien une erreur liée à champInconnu
        errors = e.errors()
        assert any("champInconnu" in str(err.get("loc", "")) for err in errors)


def test_livre_update_forbid_extra_fields():
    data = {"titre": "Titre", "champInconnu": "xx"}
    try:
        LivreUpdate(**data)
        assert False, "LivreUpdate aurait dû rejeter les champs extra"
    except ValidationError as e:
        errors = e.errors()
        assert any("champInconnu" in str(err.get("loc", "")) for err in errors)


def test_livre_create_accepts_annee_int():
    payload = LivreCreate(
        titre="Test année",
        auteur="Auteur",
        annee=1999,
        nombre_copies=2,
    )
    assert isinstance(payload.annee, int)
    assert payload.annee == 1999
