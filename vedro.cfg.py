import vedro
import vedro_fn


class Config(vedro.Config):
    default_scenarios_dir = "tests/"

    class Plugins(vedro.Config.Plugins):

        class VedroFn(vedro_fn.VedroFn):
            enabled = True
