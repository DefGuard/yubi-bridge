correct_json = '{"first_name":"Jan","last_name":"Kowalski","email":"test@test.pl"}'
wrong_key_json = '{"frst_name":"Jan","ast_name":"Kowalski","mail":"test@test.pl"}'
wrong_format_json = '{first_name":"Jan","Last_name":Kowalski","email":"test@test.pl"}'

s_key = {
    "key_id": "BC256C4D535519B8",
    "key_type": "s",
    "key": "F1617E08EC3BE9502431AE66BC256C4D535519B8",
}
a_key = {
    "key_id": "968BA0FEBFD7ADA1",
    "key_type": "a",
    "key": "E2FA8E6611FCBCE113344CED968BA0FEBFD7ADA1",
}
e_key = {
    "key_id": "7BE87A524CAF0A1C",
    "key_type": "e",
    "key": "7654DB696EE79A17AB8395F47BE87A524CAF0A1C",
}

list_keys = [
    {
        "type": "pub",
        "trust": "u",
        "length": "2048",
        "algo": "1",
        "keyid": "795FA0E3332FCEFC",
        "date": "1637936835",
        "expires": "",
        "dummy": "",
        "ownertrust": "u",
        "sig": "",
        "cap": "escaESCA",
        "issuer": "",
        "flag": "",
        "token": "",
        "hash": "",
        "curve": "",
        "compliance": "23",
        "updated": "",
        "origin": "0",
        "uids": ["marek test <test@o2.pl>"],
        "sigs": [],
        "subkeys": [
            ["BC256C4D535519B8", "s", "F1617E08EC3BE9502431AE66BC256C4D535519B8"],
            ["968BA0FEBFD7ADA1", "a", "E2FA8E6611FCBCE113344CED968BA0FEBFD7ADA1"],
            ["7BE87A524CAF0A1C", "e", "7654DB696EE79A17AB8395F47BE87A524CAF0A1C"],
        ],
        "fingerprint": "93F8CF48897937A0FB2A0856795FA0E3332FCEFC",
        "subkey_info": {
            "BC256C4D535519B8": {
                "type": "sub",
                "trust": "u",
                "length": "2048",
                "algo": "1",
                "keyid": "BC256C4D535519B8",
                "date": "1637936836",
                "expires": "",
                "dummy": "",
                "ownertrust": "",
                "uid": "",
                "sig": "",
                "cap": "s",
                "issuer": "",
                "flag": "",
                "token": "",
                "hash": "",
                "curve": "",
                "compliance": "23",
                "updated": "",
                "origin": "unavailable",
            },
            "968BA0FEBFD7ADA1": {
                "type": "sub",
                "trust": "u",
                "length": "2048",
                "algo": "1",
                "keyid": "968BA0FEBFD7ADA1",
                "date": "1637936838",
                "expires": "",
                "dummy": "",
                "ownertrust": "",
                "uid": "",
                "sig": "",
                "cap": "a",
                "issuer": "",
                "flag": "",
                "token": "",
                "hash": "",
                "curve": "",
                "compliance": "23",
                "updated": "",
                "origin": "unavailable",
            },
            "7BE87A524CAF0A1C": {
                "type": "sub",
                "trust": "u",
                "length": "2048",
                "algo": "1",
                "keyid": "7BE87A524CAF0A1C",
                "date": "1637936839",
                "expires": "",
                "dummy": "",
                "ownertrust": "",
                "uid": "",
                "sig": "",
                "cap": "e",
                "issuer": "",
                "flag": "",
                "token": "",
                "hash": "",
                "curve": "",
                "compliance": "23",
                "updated": "",
                "origin": "unavailable",
            },
        },
    }
]

public_key_asc = """-----BEGIN PGP PUBLIC KEY BLOCK-----

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
i7u4BVRJEgtqV04=
=3+aj
-----END PGP PUBLIC KEY BLOCK-----
"""
