from django.contrib.auth.hashers import PBKDF2PasswordHasher


class FastPBKDF2Hasher(PBKDF2PasswordHasher):
    """PBKDF2 com poucas iterações — senha ainda é hasheada (nunca texto puro),
    só não usa o custo alto de produção. Adequado para os ~10 mil usuários
    fake da base de demonstração; nunca deve ser usado com dados reais."""

    iterations = 4000
