# Private variables
_object_id_pattern = "^([0-9]|[a-f]){24}$"

empty_schema = {}

error_message = {
    "title": "Error message schema",
    "description" : "This is a schema that matches the error message",
    "type": "object",
    "$schema": "http://json-schema.org/draft-07/schema#",
    "properties":
    {
        "code": {
            "type": "integer",
            "title": "Error Code"
            },
        "message":{
            "type": "string",
            "title": "Error message"}
    },
    "required": ["message"]
}

payload_check_error = {
   "definitions": {},
   "$schema": "http://json-schema.org/draft-07/schema#",
   "$id": "http://example.com/root.json",
   "type": "object",
   "title": "The Root Schema",
   "required": [
      "messages"
   ],
   "properties": {
      "messages": {
         "type": "array",
         "title": "The Messages Schema",
         "items": {
            "type": "string",
            "title": "The Items Schema",
        "pattern": "^(.*)$"
      }
    }
  }
}

s2ssecret = {
   "title": "s2s secret schema",
   "description" : "This is a schema that matches the s2s secret",
   "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties":{
        "s2sSecret" : {"type":  "string"}
    },
    "required": ["s2sSecret"]
}

user = {
    "title": "user schema",
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "description": "This is a schema that matches the user object",
    "properties": {
       "role": {
          "type": "string"
       },
       "account": {
          "type": "string",
          "parttern": _object_id_pattern
       },
       "email": {
          "type": "string"
       },
       "id": {
          "type": "string"
       },
       "name": {
          "type": "string"
       },
       "secret_key": {
          "type": "string"
       },
       "status": {
          "type": "string"
       }
    },
    "required": [
       "role",
       "account",
       "email",
       "id",
       "name",
       "secret_key",
       "status"
    ]
}

replacement = {
   "title": "replacement schema",
   "$schema": "http://json-schema.org/draft-07/schema#",
   "type": "object",
   "description": "This is a schema that matches the replacement object",
   "properties": {
      "key": {
         "type": "string"
      },
      "name": {
         "type": "string"
      },
      "type": {
         "type": "string"
      },
      "value": {
         "type": "string"
      }
   },
   "required": [
      "key",
      "name",
      "type",
      "value"
   ]
}

store_apps = {
   "title": "store apps",
   "schema": "http://json-schema.org/draft-07/schema#",
   "type": "object",
   "description": "This is a schema that matches the apps schema on the store/market",
   "required": [
      "result",
      "search"
   ],
   "properties": {
      "result": {
         "type": "array",
         "items": {
            "required": [
               "company",
               "id",
               "name",
               "thumbnail"
            ],
            "properties": {
               "id": {"type": "string"},
               "company": {"type": "string"},
               "name": {"type": "string"},
               "thumbnail": {"type": "string"}
            }
         }
      },
      "search": {
         "type": "string"
      }
   }
}

notifications = {
   "title": "notifications schema",
   "$schema": "http://json-schema.org/draft-07/schema#",
   "type": "object",
   "description": "This is a schema that matches the notifications object",
   "type": "array",
   "items": 
   {
   	"type": "object",
   	"required": [
      "id",
      "message",
      "timestamp",
      "user",
      "newObj"
    ],
   "properties": 
   {
         "id": {
            "type": "string",
            "pattern": _object_id_pattern
         },
         "message": {
            "type": "string"
         },
         "timestamp": {
            "type": "string"
         },
         "user": {
            "type": "object",
            "required": [
               "_id",
               "email",
               "name"
            ],
          "properties":{
             "_id":{
                "type": "string",
                "pattern": _object_id_pattern
             },
             "email": {
                "type": "string"
             },
             "name": {
                "type": "string"
             }
          },
          "newObj": {
             "type": "object"
          }
      }
   }
   }
}

sdk = {
   "title": "sdk schema",
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "description": "This is a schema that matches the sdk object",
    "properties": {
   		"status": {
        	"type":"string"
        },
        "version": {
        	"type":"string"
        },
        "config": {
        	"type":"string"
        },
        "id": {
        	   "type":"string",
           "pattern": _object_id_pattern
        },
        "name": {
        	"type":"string"
        },
        "type": {
        	"type": "string"
        },
        "release_date": {
        	"type": "string"
        },
        "release_notes": {
        	"type": "array"
        },
        "links": {
        	"type": "object",
            "required": [
            	"get_started",
              	"sample_app"
            ],
            "properties": {
            	"get_started": {"type": "string"},
                "sample_app": {"type": "string"}
            }
        },
     	"img": {
        	"type": "string"
        },
        "download": {
        	"type": "string"
        }
   },
   "required": [
   	   "status",
         "version",
         "config",
         "id",
         "name",
         "type",
         "release_date",
         "release_notes",
         "links",
         "img",
         "downloads"
   ]
}

sdks = {
   "title": "account schema",
   "$schema": "http://json-schema.org/draft-07/schema#",
   "type": "object",
   "description": "This is a schema that matches the sdks list",
   "type": "array",
   "items":
   {
     "properties": {
   		"status": {
        	"type":"string"
        },
        "version": {
        	"type":"string"
        },
        "config": {
        	"type":"string"
        },
        "id": {
        	   "type":"string",
           "pattern": _object_id_pattern
        },
        "name": {
        	"type":"string"
        },
        "type": {
        	"type": "string"
        },
        "release_date": {
        	"type": "string"
        },
        "release_notes": {
        	"type": "array"
        },
        "links": {
        	"type": "object",
            "required": [
            	"get_started",
              	"sample_app"
            ],
            "properties": {
            	"get_started": {"type": "string"},
                "sample_app": {"type": "string"}
            }
        },
     	"img": {
        	"type": "string"
        },
        "download": {
        	"type": "string"
        }
   },
   "required": [
   	   "status",
         "version",
         "config",
         "id",
         "name",
         "type",
         "release_date",
         "release_notes",
         "links",
         "img",
         "downloads"
      ]
   }
}

accounts = {
   "title": "accounts list",
   "$schema": "http://json-schema.org/draft-07/schema#",
   "description": "This is a schema that matches accounts array",
   "type": "array",
   "items": {
      "type": "object",
      "properties":
      {
         "accountAppBlacklist":{
            "type": "array"
         },
         "address": {
            "type": "object"
         },
         "billingEntity": {
            "type": "string"
         },
         "contact": {
            "type": "object",
            "required": [
                "email",
                  "name"
            ],
            "properties":{
               "email":{
                "type": "string"
             },
               "name": {
                  "type": "string"
             }
            }
         },
         "id": {  
            "type": "string",
            "pattern": _object_id_pattern
         },
         "name": {
            "type": "string"
         },
         "sdkTermsAgreement": {
            "type": "array"
         },
         "type": {
            "type":"string"
         }
      },
      "required": [
         "accountAppBlacklist",
         "address",
         "contact",
         "id",
         "name",
         "sdkTermsAgreement",
         "type"
      ]
   }
}

account =  {
    "title": "account schema",
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "description": "This is a schema that matches the account object",
    "properties":
    {
       "accountAppBlacklist":{
          "type": "array"
       },
       "address": {
          "type": "object"
       },
       "billingEntity": {
          "type": "string"
       },
       "contact": {
          "type": "object",
          "required": [
             "email",
             "name"
          ],
          "properties":{
             "email":{
                "type": "string"
             },
             "name": {
                "type": "string"
             }
          }
       },
       "id": {  
         "type": "string",
         "pattern": _object_id_pattern
       },
       "name": {
         "type": "string"
       },
       "sdkTermsAgreement": {
          "type": "array"
       },
       "type": {
          "type":"string"
       }
    },
    "required": [
      "accountAppBlacklist",
      "address",
      "contact",
      "id",
      "name",
      "sdkTermsAgreement",
      "type"
   ]
}

adv_apps = {
   "title":"advertiser apps list",
   "$schema":"http://json-schema.org/draft-07/schema#",
   "description":"This is a schema that matches advertisers app array",
   "type": "array",
   "items": {
      "type": "object",
      "required": [
       "_id",
       "name",
       "parentAccount",
       "platform",
       "status"
     ],
     "properties":{
        "id": {
            "type":"string",
            "pattern": _object_id_pattern
         },
         "iconUrl": {
            "type": "string"
         },
         "marketId": {
            "type": "string"
         },
         "name": {
            "type": "string"
         },
         "parentAccount": {
            "type":"string",
            "pattern": _object_id_pattern
         },
         "platform": {
            "type":"string"
         },
         "status": {
            "type":"string"
         }
     }
   }
}

placements = {
   "title":"placements list",
   "$schema":"http://json-schema.org/draft-07/schema#",
   "description":"This is a schema that matches placements array",
   "type":"array",
   "items":{
      "type":"object",
      "required": [
         "id",
         "isAutoCached",
         "isSkippable",
         "name",
         "referenceID",
         "status",
         "type",
         "allowEndCards",
         "application"
      ],
      "properties":{
         "id":{
            "type":"string",
            "pattern": _object_id_pattern
         },
         "isAutoCached":{
            "type":"boolean"
         },
         "isSkippable":{
            "type":"boolean"
         },
         "name":{
            "type":"string"
         },
         "referenceID":{
            "type":"string"
         },
         "status":{
            "type":"string"
         },
         "type":{
            "type":"string"
         },
         "allowEndcards":{
            "type":"string"
         },
         "application":{
            "type":"object",
            "required":[
               "id",
               "status",
               "vungleAppId",
               "isCoppa",
               "name",
               "owner",
               "platform",
               "store"
            ],
            "properties":{
               "isCoppa":{
                  "type":"boolean"
               },
               "name":{
                  "type":"string"
               },
               "owner":{
                  "type":"string"
               },
               "platform":{
                  "type":"string"
               },
               "id":{
                  "type":"string",
                  "pattern":_object_id_pattern
               },
               "status":{
                  "type":"string"
               },
               "vungleAppId":{
                  "type":"string",
                  "pattern": _object_id_pattern
               },
               "store":{
                  "type":"object",
                  "required":[
                     "category",
                     "id",
                     "isManual",
                     "isPaid"
                  ],
                  "properties":{
                     "category":{
                        "type":"string"
                     },
                     "id":{
                        "type":"string"
                     },
                     "isManual":{
                        "type":"boolean"
                     },
                     "isPaid":{
                        "type":"boolean"
                     }
                  }
               }
            }
         }
      }
   }
}

placement = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "The Root Schema",
    "required": [
       "allowEndCards",
       "dailyDeliveryLimit",
       "id",
       "isAutoCached",
       "isFlatCPMEnabled",
       "name",
       "referenceID",
       "status",
       "supportedAdFormats",
       "type",
       "videoOrientationOverride",
       "application"
    ]  
}

placement_tags = {
   "$schema":"http://json-schema.org/draft-07/schema#",
   "type":"array",
   "title":"The Root Schema",
   "items":{
      "$id":"#/items",
      "type":"string",
      "title":"The Items Schema",
      "pattern":"^(.*)$"
   }
}

ss_placement = {
   "$schema":"http://json-schema.org/draft-07/schema#",
   "type":"object",
   "title":"Placement schema of self service",
   "required":[
      "allowEndCards",
      "application",
      "id",
      "name",
      "referenceID",
      "status",
      "type",
      "isFlatCPMEnabled",
      "videoOrientationOverride"
   ],
   "properties":{
      "allowEndCards":{
         "type":"boolean"
      },
      "id":{
         "type":"string",
         "pattern":"^([0-9]|[a-f]){24}$"
      },

      "isSkippable":{
         "type":"boolean"
      },
      "name":{
         "type":"string"
      },
      "referenceID":{
         "type":"string"
      },
      "status":{
         "type":"string"
      },
      "type":{
         "type":"string"
      },
      "isFlatCPMEnabled":{
         "type":"boolean"
      },
      "videoOrientationOverride":{
         "type":"string"
      },
      "application":{
         "type":"object",
         "required":[
            "id",
            "status",
            "vungleAppId",
            "isCoppa",
            "name",
            "owner",
            "platform",
            "store"
         ],
         "properties":{
            "isCoppa":{
               "type":"boolean"
            },
            "name":{
               "type":"string"
            },
            "owner":{
               "type":"string"
            },
            "platform":{
               "type":"string"
            },
            "id":{
               "type":"string",
               "pattern":"^([0-9]|[a-f]){24}$"
            },
            "status":{
               "type":"string"
            },
            "vungleAppId":{
               "type":"string",
               "pattern":"^([0-9]|[a-f]){24}$"
            },
            "store":{
               "type":"object",
               "required":[
                  "category",
                  "id",
                  "isManual",
                  "isPaid"
               ],
               "properties":{
                  "category":{
                     "type":"string"
                  },
                  "id":{
                     "type":"string"
                  },
                  "isManual":{
                     "type":"boolean"
                  },
                  "isPaid":{
                     "type":"boolean"
                  }
               }
            }
         }
      }
   }
}

ss_placements =  {
   "$schema":"http://json-schema.org/draft-07/schema#",
   "title":"Placements schema of self service",
   "type":"array",
   "items":{
      "type":"object",
      "required":[
         "allowEndCards",
         "application",
         "id",
         "name",
         "referenceID",
         "status",
         "type"
      ],
      "properties":{
         "allowEndCards":{
            "type":"boolean"
         },
         "id":{
            "type":"string",
            "pattern":"^([0-9]|[a-f]){24}$"
         },
         "isSkippable":{
            "type":"boolean"
         },
         "name":{
            "type":"string"
         },
         "referenceID":{
            "type":"string"
         },
         "status":{
            "type":"string"
         },
         "type":{
            "type":"string"
         },
         "application":{
            "type":"object",
            "required":[
               "id",
               "status",
               "vungleAppId",
               "isCoppa",
               "name",
               "owner",
               "platform",
               "store"
            ],
            "properties":{
               "isCoppa":{
                  "type":"boolean"
               },
               "name":{
                  "type":"string"
               },
               "owner":{
                  "type":"string"
               },
               "platform":{
                  "type":"string"
               },
               "id":{
                  "type":"string",
                  "pattern":"^([0-9]|[a-f]){24}$"
               },
               "status":{
                  "type":"string"
               },
               "vungleAppId":{
                  "type":"string",
                  "pattern":"^([0-9]|[a-f]){24}$"
               },
               "store":{
                  "type":"object",
                  "required":[
                     "category",
                     "id",
                     "isManual",
                     "isPaid"
                  ],
                  "properties":{
                     "category":{
                        "type":"string"
                     },
                     "id":{
                        "type":"string"
                     },
                     "isManual":{
                        "type":"boolean"
                     },
                     "isPaid":{
                        "type":"boolean"
                     }
                  }
               }
            }
         }
      }
   }
}

applications = {
   "title": "applications list",
   "$schema": "http://json-schema.org/draft-07/schema#",
   "description": "This is a schema that matches applications array",
   "type": "array",
   "items": 
   {
   	"type": "object",
   	"required": [
      "id",
      "name",
      "owner",
      "platform",
      "placement_count",
      "vungleAppId",
      "isCoppa",
      "store",
      "status"
    ],
   "properties": 
   {
         "id": {
            "type": "string",
            "pattern": _object_id_pattern
         },
         "name": {
            "type": "string"
         },
         "owner": {
            "type": "string",
            "pattern": _object_id_pattern
         },
         "vungleAppId": {
            "type": "string",
            "pattern": _object_id_pattern
         },
         "platform": {
         	"type": "string"
         },
         "isCoppa":{
            "type": "boolean"
         },
         "status": {
            "type": "string",
         },
         "store": {
            "type": "object",
            "required": [
               "category",
               "id",
               "isManual",
               "isPaid"
            ],
          "properties":{
             "category":{
                "type": "string"
             },
             "id": {
                "type": "string"
             },
             "isManual": {
                "type": "boolean"
             },
             "isPaid": {
                "type": "boolean"
             }
          }
      }
   }
   }
}

application = {
   "title": "Application schema",
   "$schema": "http://json-schema.org/draft-07/schema#",
   "type":"object",
   "required":[  
      "isCoppa",
      "name",
      "owner",
      "platform",
      "store",
      "enableABTesting",
      "supportedTemplateTypes",
      "adType",
      "appFilters",
      "connection",
      "deliveryType",
      "enableGDPR",
      "enableSubServerCost",
      "forceView",
      "id",
      "logging",
      "maxVideoLength",
      "minOs",
      "orientation",
      "replacements",
      "revShare",
      "status",
      "subServerCost",
      "tagFilters",
      "tags",
      "vungleAppId"
   ],
   "properties":{  
      "isCoppa":{  
         "type":"boolean",
         "default": False
      },
      "name":{  
         "type":"string",
         "pattern":"^(.*)$"
      },
      "owner":{  
         "type":"string",
         "pattern": _object_id_pattern
      },
      "platform":{  
         "type":"string",
         "enum":[  
            "ios",
            "windows",
            "amazon",
            "android"
         ],
         "minLenght":3
      },
      "store":{  
         "type":"object",
         "required":[  
            "category",
            "id"
         ],
         "properties":{  
            "category":{  
               "type":"string"
            },
            "id":{  
               "type":"string"
            }
         }
      },
      "enableABTesting":{  
         "type":"boolean"
      },
      "supportedTemplateTypes":{  
         "type":"array",
         "items":{  
            "type":"string",
            "minLength":1
         }
      },
      "adType":{  
         "type":"string",
         "pattern":"^(.*)$"
      },
      "appFilters":{  
         "type":"object",
         "required":[  
            "blacklist",
            "whitelist"
         ],
         "properties":{  
            "blacklist":{  
               "type":"array"
            },
            "whitelist":{  
               "type":"array"
            }
         }
      },
      "connection":{  
         "type":"string",
         "pattern":"^(.*)$"
      },
      "dailyDeliveryLimit":{  
         "type":"integer",
         "default":20
      },
      "deliveryType":{  
         "type":"string",
         "pattern":"^(.*)$"
      },
      "enableGDPR":{  
         "type":"boolean"
      },
      "enableSubServerCost":{  
         "type":"boolean"
      },
      "forceView":{  
         "type":"object",
         "required":[  
            "nonRewarded",
            "rewarded"
         ],
         "properties":{  
            "nonRewarded":{  
               "type":"boolean"
            },
            "rewarded":{  
               "type":"boolean"
            }
         }
      },
      "id":{  
         "type":"string",
         "pattern": _object_id_pattern
      },
      "incentivizedView":{  
         "type":"string",
         "pattern":"^(\\d)*$",
         "default":"9999"
      },
      "limitCreativeCap":{  
         "type":"boolean"
      },
      "logging":{  
         "type":"object",
         "required":[  
            "install",
            "request"
         ],
         "properties":{  
            "install":{  
               "type":"boolean"
            },
            "request":{  
               "type":"boolean"
            }
         }
      },
      "maxVideoLength":{  
         "type":"integer"
      },
      "minOs":{  
         "type":"number"
      },
      "nonIncentivizedView":{  
         "type":"string",
         "pattern":"^(\\d)*$"
      },
      "orientation":{  
         "type":"string",
         "enum":[  
            "both",
            "landscape",
            "portrait"
         ]
      },
      "replacements":{  
         "type":"array",
         "items":{  
            "type":"object",
            "required":[  
               "key",
               "value"
            ],
            "properties":{  
               "key":{  
                  "type":"string",
                  "pattern":"^(.*)"
               },
               "value":{  
                  "type":"string",
                  "pattern":"^(.*)"
               }
            }
         }
      },
      "revShare":{  
         "type":"number"
      },
      "status":{  
         "type":"string",
         "enum":[  
            "test",
            "active",
            "inactive"
         ]
      },
      "subServerCost":{  
         "type":"number"
      },
      "tagFilters":{  
         "type":"object",
         "required":[  
            "blacklist",
            "whitelist"
         ],
         "properties":{  
            "blacklist":{  
               "type":[  
                  "string",
                  "null",
                  "array"
               ]
            },
            "whitelist":{  
               "type":[  
                  "string",
                  "null",
                  "array"
               ]
            }
         }
      },
      "tags":{  
         "type":[  
            "array",
            "null"
         ],
         "items":{  
            "type":"string"
         }
      },
      "vungleAppId":{  
         "type":"string",
         "pattern": _object_id_pattern
      }
   }
}

ss_applications = {
   "title":"Applications schema of SS",
   "$schema":"http://json-schema.org/draft-07/schema#",
   "type":"array",
   "items":{
      "type":"object",
      "required":[
         "isCoppa",
         "name",
         "platform",
         "store",
         "id",
         "owner",
         "status",
         "vungleAppId"
      ],
      "properties":{
         "isCoppa":{
            "type":"boolean",
            "default": False
         },
         "name":{
            "type":"string",
            "pattern":"^(.*)$"
         },
         "owner":{
            "type":"string",

         },
         "platform":{
            "type":"string",
            "enum":[
               "ios",
               "windows",
               "amazon",
               "android"
            ],
            "minLenght":3
         },
         "store":{
            "type":"object",
            "required":[
               "category",
               "id"
            ],
            "properties":{
               "category":{
                  "type":"string"
               },
               "id":{
                  "type":"string"
               }
            }
         },
         "id":{
            "type":"string",
            "pattern": _object_id_pattern
         },
         "maxVideoLength":{
            "type":"integer"
         }
      }
   }
}

ss_application = {
   "title": "Application schema of pub self-service",
   "$schema":"http://json-schema.org/draft-07/schema#",
   "type":"object",
   "required":[
      "isCoppa",
      "name",
      "platform",
      "store",
      "id",
      "owner",
      "status",
      "vungleAppId",
      "connection",
      "forceView",
      "maxVideoLength",
      "minOs",
      "orientation",
      "tagFilters"
   ],
   "properties":  {
      "isCoppa":  {
         "type":  "boolean",
         "default": False
      },
      "name":  {
         "type":  "string",
         "pattern":  "^(.*)$"
      },
      "owner": {
         "type":  "string",
         "pattern"   :_object_id_pattern
      },
      "platform": {
         "type":"string",
         "enum":[
            "ios",
            "windows",
            "amazon",
            "android"
         ],
         "minLenght":3
      },
      "store":{
         "type":"object",
         "required":[
            "category",
            "id"
         ],
         "properties":{
            "category":{
               "type":"string"
            },
            "id":{
               "type":"string"
            }
         }
      },
      "connection":{
         "type":"string",
         "pattern":"^(.*)$"
      },
      "forceView":{
         "type":"object",
         "required":[
            "nonRewarded",
            "rewarded"
         ],
         "properties":{
            "nonRewarded":{
               "type":"boolean"
            },
            "rewarded":{
               "type":"boolean"
            }
         }
      },
      "id":{
         "type":  "string",
         "pattern": _object_id_pattern
      },
      "vungleAppId":{
         "type":  "string",
         "pattern": _object_id_pattern
      },
      "maxVideoLength":{
         "type":"integer"
      },
      "minOs":{
         "type":  "number"
      },
      "status": {
         "type": "string"
      },
      "orientation":{
         "type":"string",
         "enum":[
            "both",
            "landscape",
            "portrait"
         ]
      },
      "tagFilters":{
         "type":"object",
         "required":[
            "blacklist"
         ],
         "properties":{
            "blacklist":{
               "type":[
                  "string",
                  "null",
                  "array"
               ]
            }
         }
      }
   }
}