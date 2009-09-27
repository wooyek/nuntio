from ragendja.settings_post import settings
settings.add_app_media('combined-%(LANGUAGE_DIR)s.css',
    'nuntio/css/reset.css',
    'nuntio/css/FreshPick.css',
#    'nuntio/lang-%(LANGUAGE_DIR)s.css',
)
settings.add_app_media('combined-print-%(LANGUAGE_DIR)s.css',
    'nuntio/css/print.css',
)
#settings.add_app_media('ie.css',
#    'nuntio/ie.css',
#)