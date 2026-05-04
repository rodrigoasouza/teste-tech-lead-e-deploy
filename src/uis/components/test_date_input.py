from datetime import date
from unittest.mock import MagicMock

import pytest

from src.uis.components.date_input import DateInput, DateRangePicker


def test_date_input_valid_format():
    # Mocking nicegui ui.input behavior
    input_comp = DateInput("Teste", value="15/05/2023")
    result = input_comp.validate_and_get()
    assert result == date(2023, 5, 15)


def test_date_input_invalid_format():
    input_comp = DateInput("Teste", value="2023-05-15")
    with pytest.raises(ValueError, match="inválida ou incompleta. Use DD/MM/AAAA"):
        input_comp.validate_and_get()


def test_date_input_required_empty():
    input_comp = DateInput("Teste", value="", required=True)
    with pytest.raises(ValueError, match="é obrigatório"):
        input_comp.validate_and_get()


def test_date_input_not_required_empty():
    input_comp = DateInput("Teste", value="", required=False)
    result = input_comp.validate_and_get()
    assert result is None


def test_date_range_valid():
    # Precisamos de um mock para ui.row() ou rodar em contexto nicegui
    # Mas como estamos testando a lógica de validação que acessa self.start_input.value
    # podemos instanciar e setar os valores.
    with MagicMock():  # Mock para evitar erros de renderização do NiceGUI se houver
        range_picker = DateRangePicker()
        range_picker.start_input.value = "01/01/2023"
        range_picker.end_input.value = "31/12/2023"
        start, end = range_picker.validate_and_get()
        assert start == date(2023, 1, 1)
        assert end == date(2023, 12, 31)


def test_date_range_invalid_order():
    with MagicMock():
        range_picker = DateRangePicker()
        range_picker.start_input.value = "31/12/2023"
        range_picker.end_input.value = "01/01/2023"
        with pytest.raises(ValueError, match="não pode ser anterior à"):
            range_picker.validate_and_get()


def test_date_range_out_of_bounds():
    with MagicMock():
        range_picker = DateRangePicker()
        range_picker.start_input.value = "01/01/1899"
        range_picker.end_input.value = "01/01/2023"
        with pytest.raises(ValueError, match="fora do intervalo permitido"):
            range_picker.validate_and_get()
