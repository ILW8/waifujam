# BASE_PATH = '/home/daohe/waifujam_transcodes'
import json
from collections import defaultdict

BASE_PATH = '/Volumes/970evo/wjvids'
import hashlib

hashlib.md5("whatever your string is".encode('utf-8')).hexdigest()

import os

if __name__ == '__main__':
    # mapping = defaultdict(defaultdict)
    # for root, _, files in os.walk(BASE_PATH):
    #     for file in files:
    #         if not file.endswith(".mp4"):
    #             continue
    #
    #         diff, segment = file.split('.')[:2]
    #
    #         prefix = hashlib.sha1(
    #             hashlib.md5('.'.join(file.split('.')[:2]).encode('utf-8')).digest()
    #         ).hexdigest()
    #         mapping[diff][segment] = prefix
    #
    #         new_name = f"{prefix}.{'.'.join(file.split('.')[2:])}"
    #         print(f"old name: {file}  | new name: {new_name}")
    #         os.rename(os.path.join(root, file), os.path.join(root, new_name))
    #
    # print(json.dumps(mapping))

    AAAA = {"quiet forest": {"Ro2": "a1ae6cda163d972bcaca25cc60457381609e7db4",
                             "Ro4": "b2e6b4cc8174cac4b7147a803d93f5394e306a37",
                             "Ro8": "0090499bc2768512fa9aab5016e56999fb094a73",
                             "Full": "e535e0099260abe7c87add91ef02231ddc91b219",
                             "Ro16": "6ed4fba46cb89fbaf141932fd03f1460279b310c"},
            "grandmother fighting": {"Ro4": "32f6f755795d00dcc6332b019a13fcd52f9d340c",
                                     "Ro2": "f903210e483b3d0f5d1f5afcdc52764d4cd50145",
                                     "Ro16": "579bd91db493f1153bb6742743d860c1eb318bb7",
                                     "Ro8": "a35b10b8d6e6b44cb7fa706b7fa90c98eb1e0b83",
                                     "Full": "b116235c0a079ca57b4b0da149531ad66b108307"},
            "pressure hurt": {"Full": "2cc26bfbee46568c99c3ce0b5d2c0644010c84bd",
                              "Ro4": "25e2aed6811ec9f21a4a5e87d094bc9e4116c266",
                              "Ro16": "0bf781112b0326a997116a3aba2f06ffece7b4fe",
                              "Ro2": "51531e6728ebceedb3842c8b80a76e0c9e8cdb1a",
                              "Ro8": "2908ab90f1a9e04ae1b7b6b49c8d680e7fe39294"},
            "appropriate especially": {"Full": "fb07d3bc5f535c13f0559de4731e75c6e31d7b91",
                                       "Ro16": "1f918f3beb0fb97f9f8c48f5b722430b30ba9395",
                                       "Ro8": "9c9f99cfd39ae53f695f5df4383606a4bed8cc03",
                                       "Ro2": "b7cd58cdb366cd2775fa660a6984c9efd0452114",
                                       "Ro4": "0107843954c3fd26864613f878040678bfa88acd"},
            "distance fellow": {"Ro8": "a8bcab0682e3b051e840764c4c388fa7fb7f33de",
                                "Ro4": "ba70f39ccd947c82b0d93265f4b1889f64f90d34",
                                "Ro2": "3b7752695c51d07db3156f312941f74789ecd0dc",
                                "Ro16": "35675e246a1751cbe8994c6b13128872765636e1",
                                "Full": "9b35bac2e03025fd5be72de10ae8384a4232ef4a"},
            "star hamster": {"Ro2": "ed0e3ba93db96af2ed9437709bb7e7b582bdc4fe",
                             "Ro8": "69319e99dc0817beb64b3d531f8f81486d500338",
                             "Full": "af3b24fd4a641302e7a125534e4beadb5c5f0d33",
                             "Ro16": "754f173d0aa4b59af9cfef03c77327b609bf1f40",
                             "Ro4": "89c34027ae8a84a14679f70027209956e83d49b8"},
            "regular flower": {"Full": "0de65aab8af75def98c63ac873e6278458a87341",
                               "Ro16": "2dff360641e775651e9551be6a84fc3215715bab",
                               "Ro8": "6ef39985086984df6cc10d9af369f7037d704f59",
                               "Ro2": "1c7a96aafc6e9556ef91e013245c92e0d5c619a3",
                               "Ro4": "7b93b40b46d4716dbee36ff54784e3d6c771f4a4"},
            "under balloon": {"Ro4": "689e1a3c7c947e3c4873109b7cea99998546bc3c",
                              "Ro8": "4385f37ceeff0dcf172068fc3255021424f93274",
                              "Ro16": "2c52dd973baff430c09ae1d054d84eec8bbce0b5",
                              "Ro2": "b439ec1de54228d985ec8399cf0a7a6fd15bfa73",
                              "Full": "444cfc0cab7aaa53cc3cbcc34a7bd272bef62ada"},
            "bent does": {"Ro8": "30f6009f9c2c05741e42ef94d9d41fc8ba0e5756",
                          "Ro2": "3239566b9fbb64ff11eef69638f6101471142812",
                          "Ro4": "a190860598b29836edfd2fbeb610841a5ff384c3",
                          "Ro16": "eb8d6f34385cb75174e2edfae8b238d188975d26",
                          "Full": "720497f930d8f597d64bd74239d8cb248454d1a7"},
            "busy continued": {"Ro4": "94b8d0603b4ea1eeaeb7d9d27379781238f08cfb",
                               "Ro2": "b39c15d09989392c9feab9c432dee6b4fb22b2b9",
                               "Ro8": "4c2f7138b6db303d6f1be9097b1d6b169682772d",
                               "Ro16": "cafd5f3535a5f99925841e516f0fb0cf80127f78",
                               "Full": "fe42685e6bb3f34173865884447a29240c0e2361"},
            "tear rainbow": {"Ro16": "a631a4bd26cfe454e7318ccadbf32d4c3ff6123e",
                             "Full": "a694a20bc098c07d07741ba77dba78722eb36cb5",
                             "Ro8": "4f00444098ac1e7d5a1d571c64af8a5b1e90e28e",
                             "Ro2": "cfc2828d90cfabb9e53a25b222d9b6ab6e87c68f",
                             "Ro4": "9daf3ec8be9f5b471e1febc406466d17bf0ba39c"},
            "summer fifteen": {"Ro16": "2bd274e66108107c5ad121f188715be6dd9bbacd",
                               "Ro4": "d7bfc319d00ef9045bf9a968056a8919f41a3f28",
                               "Ro2": "860b4bab4960322c11a67a2e392c1e633dd15c46",
                               "Full": "abb933553c0a3c2e0556b2f438c6b8616ad080e3",
                               "Ro8": "408b897163d38822c2019b07a14b6560c7efa3ac"},
            "pine touch": {"Ro8": "c3706313903e2b6667687dacdc015bbc35616afd",
                           "Ro16": "6121d64cc81dc6f6df809032b26febd696b15521",
                           "Ro2": "a49a6aa1fedd8eabd81ddb72dbff22d6fc59236c",
                           "Full": "01fe6f5dc8d94474f78c3e9686e123e784d216ac",
                           "Ro4": "6860141f96545e204d1124c0d6deaf192306c642"},
            "clear watercress": {"Ro4": "f39b78cf0bb26c3aa956c236d796c6db7611b915",
                                 "Ro16": "2ed288b1c739693b4f8c10ef261af15a1e7bc8ad",
                                 "Ro2": "f3620871fc17b157370181342317c30f2fd21e35",
                                 "Ro8": "edddadd8e006c37bb5d33d4f169473b2f0c17f52",
                                 "Full": "443f9c85b862d18dff5165880f2f081490ac8ae2"},
            "round cloud": {"Ro16": "d7b6c905d7871801413a2e1d2be7ddb3d8aea6f0",
                            "Ro4": "5a259dc671e1688f689dd447f1a3b538383034be",
                            "Full": "3e1d9025c3903cc63dcac72389bef05f4709ef3c",
                            "Ro8": "a61fcac9cd603e92eeeb261ea4a05af7b5b145a4",
                            "Ro2": "a8f50345c62cee37328562042f7e6df0058864de"},
            "time article": {"Ro4": "a111d7a76055af4aaf47e4b1d1db1dba99ffff1f",
                             "Ro16": "e542ad38dfd073f4f024c2dacc8d982545743a3a",
                             "Ro8": "f046a07b65f84605967e33b1e9e3d5b0ad7857d7",
                             "Ro2": "3af3b5cbb8e38d4bddaf270e0bd7d622b4573657",
                             "Full": "389dfc4e9e342682fa503888a3beef1e36742f1f"}}

    MAPS_META = {0: {'title': 'appropriate especially',
                     'videos': {0: 'https://example.com/v0s0',
                                1: 'https://example.com/v0s0',
                                2: 'https://example.com/v0s2'}},
                 1: {'title': 'regular flower',
                     'videos': {0: 'https://example.com/v1s0',
                                1: 'https://example.com/v1s0',
                                2: 'https://example.com/v1s2'}},
                 2: {'title': 'distance fellow',
                     'videos': {0: 'https://example.com/v2s0',
                                1: 'https://example.com/v2s0',
                                2: 'https://example.com/v2s2'}},
                 3: {'title': 'busy continued',
                     'videos': {0: 'https://example.com/v3s0',
                                1: 'https://example.com/v3s0',
                                2: 'https://example.com/v3s2'}},
                 4: {'title': 'tear rainbow',
                     'videos': {0: 'https://example.com/v4s0',
                                1: 'https://example.com/v4s0',
                                2: 'https://example.com/v4s2'}},
                 5: {'title': 'under balloon',
                     'videos': {0: 'https://example.com/v5s0',
                                1: 'https://example.com/v5s0',
                                2: 'https://example.com/v5s2'}},
                 6: {'title': 'round cloud',
                     'videos': {0: 'https://example.com/v6s0',
                                1: 'https://example.com/v6s0',
                                2: 'https://example.com/v6s2'}},
                 7: {'title': 'summer fifteen',
                     'videos': {0: 'https://example.com/v7s0',
                                1: 'https://example.com/v7s0',
                                2: 'https://example.com/v7s2'}},
                 8: {'title': 'star hamster',
                     'videos': {0: 'https://example.com/v8s0',
                                1: 'https://example.com/v8s0',
                                2: 'https://example.com/v8s2'}},
                 9: {'title': 'bent does',
                     'videos': {0: 'https://example.com/v9s0',
                                1: 'https://example.com/v9s0',
                                2: 'https://example.com/v9s2'}},
                 10: {'title': 'grandmother fighting',
                      'videos': {0: 'https://example.com/v10s0',
                                 1: 'https://example.com/v10s0',
                                 2: 'https://example.com/v10s2'}},
                 11: {'title': 'quiet forest',
                      'videos': {0: 'https://example.com/v11s0',
                                 1: 'https://example.com/v11s0',
                                 2: 'https://example.com/v11s2'}},
                 12: {'title': 'clear watercress',
                      'videos': {0: 'https://example.com/v12s0',
                                 1: 'https://example.com/v12s0',
                                 2: 'https://example.com/v12s2'}},
                 13: {'title': 'pine touch',
                      'videos': {0: 'https://example.com/v13s0',
                                 1: 'https://example.com/v13s0',
                                 2: 'https://example.com/v13s2'}},
                 14: {'title': 'time article',
                      'videos': {0: 'https://example.com/v14s0',
                                 1: 'https://example.com/v14s0',
                                 2: 'https://example.com/v14s2'}},
                 15: {'title': 'pressure hurt',
                      'videos': {0: 'https://example.com/v15s0',
                                 1: 'https://example.com/v15s0',
                                 2: 'https://example.com/v15s2'}}}

    new_meta = {}
    for key in AAAA:
        # yolo
        for meta_key, meta_item in MAPS_META.items():
            if meta_item['title'] == key:
                new_meta[meta_key] = meta_item
                new_meta[meta_key]['videos'] = {
                    0: AAAA[key]["Ro16"],
                    1: AAAA[key]["Ro8"],
                    2: AAAA[key]["Ro4"],
                    3: AAAA[key]["Ro2"],
                    4: AAAA[key]["Full"]
                }
    from pprint import pprint
    pprint({k: v for k, v in sorted(new_meta.items(), key=lambda x: x[0])})
