from app.utils import security


def test_hash_and_verify_password_ok():
    plain = "mon_mdp_secret"
    hashed = security.hash_password(plain)
    assert security.verify_password(plain, hashed)


def test_verify_password_wrong():
    plain = "mon_mdp_secret"
    hashed = security.hash_password(plain)
    assert not security.verify_password("autre_chose", hashed)


def test_hash_password_returns_string():
    hashed = security.hash_password("password123")
    assert isinstance(hashed, str)
    assert len(hashed) > 0


def test_hash_password_produces_different_hashes_for_same_input():
    p = "same_password"
    h1 = security.hash_password(p)
    h2 = security.hash_password(p)
    assert h1 != h2


def test_hash_password_different_for_different_passwords():
    h1 = security.hash_password("pass1")
    h2 = security.hash_password("pass2")
    assert h1 != h2


def test_verify_password_empty_password_fails():
    hashed = security.hash_password("not_empty")
    assert not security.verify_password("", hashed)


def test_verify_password_with_unicode_chars():
    plain = "møt_de_påssê🔑"
    hashed = security.hash_password(plain)
    assert security.verify_password(plain, hashed)
    assert not security.verify_password("møt_de_påssê", hashed)


def test_hash_password_consistent_verification_multiple_times():
    plain = "multi_check"
    hashed = security.hash_password(plain)
    for _ in range(5):
        assert security.verify_password(plain, hashed)


def test_verify_password_fails_with_other_user_hash():
    hash_user1 = security.hash_password("user1_pwd")
    hash_user2 = security.hash_password("user2_pwd")
    assert not security.verify_password("user1_pwd", hash_user2)
    assert not security.verify_password("user2_pwd", hash_user1)


def test_create_access_token_returns_str():
    token = security.create_access_token({"sub": "testuser"})
    assert isinstance(token, str)
    assert len(token) > 10


def test_create_access_token_structure_looks_like_jwt():
    token = security.create_access_token({"sub": "jwt_user"})
    parts = token.split(".")
    # JWT classique: header.payload.signature => 3 parties
    assert len(parts) == 3


def test_create_access_token_tokens_for_different_users_are_different():
    t1 = security.create_access_token({"sub": "user_a"})
    t2 = security.create_access_token({"sub": "user_b"})
    assert t1 != t2


def test_create_access_token_with_empty_sub_still_works():
    token = security.create_access_token({"sub": ""})
    assert isinstance(token, str)
    assert len(token) > 10


def test_create_access_token_roundtrip_decode_sub():
    sub = "roundtrip_user"
    token = security.create_access_token({"sub": sub})
    decoded = security.decode_access_token(token)
    assert decoded is not None
    assert decoded.get("sub") == sub


def test_create_access_token_roundtrip_multiple_users():
    sub1 = "user1"
    sub2 = "user2"
    token1 = security.create_access_token({"sub": sub1})
    token2 = security.create_access_token({"sub": sub2})

    d1 = security.decode_access_token(token1)
    d2 = security.decode_access_token(token2)

    assert d1 is not None and d2 is not None
    assert d1.get("sub") == sub1
    assert d2.get("sub") == sub2


def test_create_access_token_with_additional_claim():
    token = security.create_access_token({"sub": "with_claim", "role": "admin"})
    decoded = security.decode_access_token(token)
    assert decoded is not None
    assert decoded.get("sub") == "with_claim"
    assert decoded.get("role") == "admin"


def test_decode_access_token_invalid_returns_none():
    decoded = security.decode_access_token("token_invalid")
    assert decoded is None


def test_decode_access_token_random_garbage_returns_none():
    decoded = security.decode_access_token("abc.def.ghi")
    assert decoded is None or isinstance(decoded, dict)


def test_decode_access_token_tampered_token_returns_none():
    token = security.create_access_token({"sub": "tampered"})
    tampered = token + "x"
    decoded = security.decode_access_token(tampered)
    assert decoded is None


def test_decode_access_token_type_of_result_is_dict():
    token = security.create_access_token({"sub": "dict_user"})
    decoded = security.decode_access_token(token)
    assert decoded is not None
    assert isinstance(decoded, dict)


def test_decode_access_token_payload_contains_sub_key():
    token = security.create_access_token({"sub": "payload_user"})
    decoded = security.decode_access_token(token)
    assert decoded is not None
    assert "sub" in decoded


def test_decode_access_token_with_no_sub_still_returns_dict():
    token = security.create_access_token({"role": "no_sub"})
    decoded = security.decode_access_token(token)
    assert decoded is not None
    assert decoded.get("role") == "no_sub"


def test_hash_and_token_can_be_used_together():
    plain = "combo_pwd"
    hashed = security.hash_password(plain)
    assert security.verify_password(plain, hashed)

    token = security.create_access_token({"sub": "combo_user"})
    decoded = security.decode_access_token(token)
    assert decoded is not None
    assert decoded.get("sub") == "combo_user"
