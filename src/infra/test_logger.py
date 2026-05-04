import io
import logging

from src.infra.logger import get_logger


def test_logger_masking():
    logger = get_logger("TestLogger")

    # Captura a saída do stdout
    output = io.StringIO()
    handler = logging.StreamHandler(output)
    # Adicionamos o mesmo filtro que o logger.py usa
    from src.infra.logger import SecretMaskingFilter

    handler.addFilter(SecretMaskingFilter())
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    # Testa máscara de Google API Key
    logger.info("Minha chave é AIzaSyD9tSrke72ndk384kdls93ksld02ksld01")

    # Testa máscara de password
    logger.info("A senha do banco é password='minha_senha_super_secreta'")

    log_content = output.getvalue()
    print(f"Log Output:\n{log_content}")

    assert "AIzaSyD" not in log_content
    assert "minha_senha_super_secreta" not in log_content
    assert "***MASKED***" in log_content


if __name__ == "__main__":
    test_logger_masking()
    print("Logger masking test PASSED!")
