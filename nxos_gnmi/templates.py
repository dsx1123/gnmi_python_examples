class Template:
    NATIVE = "device:System"

    BD = {
        "prefix": NATIVE,
        "update_template": """
        {
            "bd-items": {
                "bd-items": {
                    "BD-list": [
                        {
                            "accEncap": "vxlan-{{ vni }}",
                            "fabEncap": "vlan-{{ vlan_id }}",
                            "name": "{{ name }}"
                        }
                    ]
                }
            }
        }
        """,
        "delete_template": [
            "device:/System/bd-items/bd-items/BD-list[fabEncap=vlan-{{ vlan_id }}]",
        ],
    }

    SVI = {
        "prefix": NATIVE,
        "update_template": """
        {
        "hmm-items": {
            "fwdinst-items": {
                "if-items": {
                    "FwdIf-list": [
                        {
                            "id": "vlan{{ vlan_id }}",
                            "mode": "anycastGW"
                        }
                    ]
                }
            }
        },
        "intf-items": {
            "svi-items": {
                "If-list": [
                    {
                        "adminSt": "up",
                        "id": "vlan{{ vlan_id }}",
                        "rtvrfMbr-items": {
                            "tDn": "/System/inst-items/Inst-list[name='{{ vrf_name }}']"
                        }
                    }
                ]
            }
        },
        "ipv4-items": {
            "inst-items": {
                "dom-items": {
                    "Dom-list": [
                        {
                            "if-items": {
                                "If-list": [
                                    {
                                        "addr-items": {
                                            "Addr-list": [
                                                {
                                                    "addr": "{{ gw_ip_address }}",
                                                    "pref": "0",
                                                    "tag": "12345",
                                                    "type": "primary"
                                                }
                                            ]
                                        },
                                        "id": "vlan{{ vlan_id }}"
                                    }
                                ]
                            },
                            "name": "{{ vrf_name }}"
                        }
                    ]
                }
            }
        }
        }
        """,
        "delete_template": [
            "device:/System/intf-items/If-list[id=vlan{{ vlan_id }}]",
        ],
    }

    NVE = {
        "prefix": NATIVE,
        "update_template": """
        {
            "eps-items": {
                "epId-items": {
                    "Ep-list": [
                        {
                            "epId": "1",
                            "nws-items": {
                                "vni-items": {
                                    "Nw-list": [
                                        {
                                            "isLegacyMode": "false",
                                            "mcastGroup": "{{ mcast_group }}",
                                            "vni": "{{ vni }}"
                                        }
                                    ]
                                }
                            }
                        }
                    ]
                }
            }
        }
        """,
        "delete_template": [
            "device:/System/eps-items/epId-items/Ep-list/nws-items/vni-items/Nw-list[vni={{ vni }}]",
        ],
    }

    EVPN = {
        "prefix": NATIVE,
        "update_template": """
        {
            "evpn-items": {
                "adminSt": "enabled",
                "bdevi-items": {
                    "BDEvi-list": [
                        {
                            "encap": "vxlan-{{ vni }}",
                            "rd": "rd:unknown:0:0",
                            "rttp-items": {
                                "RttP-list": [
                                    {
                                        "ent-items": {
                                            "RttEntry-list": [
                                                {
                                                    "rtt": "route-target:unknown:0:0"
                                                }
                                            ]
                                        },
                                        "type": "export"
                                    },
                                    {
                                        "ent-items": {
                                            "RttEntry-list": [
                                                {
                                                    "rtt": "route-target:unknown:0:0"
                                                }
                                            ]
                                        },
                                        "type": "import"
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        }
        """,
        "delete_template": [
            "device:/System/eps-items/epId-items/Ep-list/nws-items/vni-items/Nw-list[vni={{ vni }}]",
        ],
    }

    INTF = {
        "prefix": NATIVE,
        "update_template": """
        {
            "intf-items": {
                "phys-items": {
                    "PhysIf-list": [
                        {
                            "id": "{{ name }}",
                            "trunkVlans": "{{ trunk_allowed_vlan | join(',') }}"
                        }
                    ]
                }
            }
        }
        """,
        "delete_template": [],
    }
