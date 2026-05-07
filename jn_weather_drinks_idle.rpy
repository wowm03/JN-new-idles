# jn_weather_drinks_idle.rpy
# Just Natsuki 1.3.5-compatible weather drink idle submod
# Corrected full replacement with desk auto-scale/positioning.
#
# Install this file as:
#   game/Submods/jn_weather_drinks_idle_test/jn_weather_drinks_idle.rpy
#
# Required assets, preferred names:
#   game/Submods/jn_weather_drinks_idle_test/assets/hot_chocolate.png
#   game/Submods/jn_weather_drinks_idle_test/assets/strawberry_cream_milkshake.png
#
# Optional milkshake fallback name also supported:
#   game/Submods/jn_weather_drinks_idle_test/assets/milkshake.png
#
# Test with the debug button or console:
#   jump idle_weather_hot_chocolate
#   jump idle_weather_milkshake
#
# This file uses spaces only. Do not paste tabs into it. Use 4 spaces per indent.

init -10 python:
    import datetime
    import store

    # -------------------------------------------------------------------------
    # Safe constants/fallbacks
    # -------------------------------------------------------------------------

    if not hasattr(store, "JN_BLACK_ZORDER"):
        store.JN_BLACK_ZORDER = 100

    if not hasattr(store, "JN_PROP_ZORDER"):
        store.JN_PROP_ZORDER = 10

    if "drawer" not in globals():
        drawer = None

    # -------------------------------------------------------------------------
    # Asset paths with safe fallback support
    # -------------------------------------------------------------------------

    JN_WD_ASSET_DIR = "Submods/jn_weather_drinks_idle_test/assets/"

    JN_WD_HOT_CHOCOLATE_IMAGE_PATH = JN_WD_ASSET_DIR + "hot_chocolate.png"

    JN_WD_MILKSHAKE_IMAGE_PATH = JN_WD_ASSET_DIR + "strawberry_cream_milkshake.png"
    if not renpy.loadable(JN_WD_MILKSHAKE_IMAGE_PATH):
        if renpy.loadable(JN_WD_ASSET_DIR + "milkshake.png"):
            JN_WD_MILKSHAKE_IMAGE_PATH = JN_WD_ASSET_DIR + "milkshake.png"

    # -------------------------------------------------------------------------
    # Persistent setup
    # -------------------------------------------------------------------------

    if not hasattr(persistent, "jn_weather_drinks_enabled"):
        persistent.jn_weather_drinks_enabled = True

    # Important fix: this variable may exist but be None from an earlier test.
    if not hasattr(persistent, "jn_weather_drinks_last_day") or not isinstance(persistent.jn_weather_drinks_last_day, dict):
        persistent.jn_weather_drinks_last_day = {}

    if not hasattr(persistent, "jn_weather_drinks_last_weather") or persistent.jn_weather_drinks_last_weather is None:
        persistent.jn_weather_drinks_last_weather = "unknown"

    # -------------------------------------------------------------------------
    # Settings
    # -------------------------------------------------------------------------

    # Predetermined time she keeps/enjoys each drink during the idle.
    # Increase these after testing if you want longer drink idles.
    JN_WD_HOT_CHOCOLATE_ENJOY_TIME = 20
    JN_WD_MILKSHAKE_ENJOY_TIME = 20

    # Set these to False if you want the drinks to repeat more than once per day.
    JN_WD_HOT_CHOCOLATE_ONCE_PER_DAY = True
    JN_WD_MILKSHAKE_ONCE_PER_DAY = True

    # Daytime fallback: 6 AM to 6 PM.
    JN_WD_DAY_START_HOUR = 6
    JN_WD_DAY_END_HOUR = 18

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    def jn_wd_now():
        return datetime.datetime.now()

    def jn_wd_today_key():
        return jn_wd_now().strftime("%Y-%m-%d")

    def jn_wd_reset_last_day_if_needed():
        if not hasattr(persistent, "jn_weather_drinks_last_day") or not isinstance(persistent.jn_weather_drinks_last_day, dict):
            persistent.jn_weather_drinks_last_day = {}

    def jn_wd_is_daytime():
        hour = jn_wd_now().hour
        return JN_WD_DAY_START_HOUR <= hour < JN_WD_DAY_END_HOUR

    def jn_wd_to_weather_text(value):
        if value is None:
            return ""

        try:
            if hasattr(value, "name"):
                return str(value.name).lower()
        except Exception:
            pass

        try:
            if hasattr(value, "weather_type"):
                return str(value.weather_type).lower()
        except Exception:
            pass

        try:
            if hasattr(value, "reference_name"):
                return str(value.reference_name).lower()
        except Exception:
            pass

        try:
            return str(value).lower()
        except Exception:
            return ""

    def jn_wd_get_weather_text():
        candidates = []

        # Common store/global weather variable names.
        for name in (
            "jn_current_weather",
            "current_weather",
            "weather",
            "mas_current_weather",
            "current_background_weather",
            "jn_current_background_weather",
        ):
            try:
                if hasattr(store, name):
                    candidates.append(getattr(store, name))
            except Exception:
                pass

        # Common persistent weather variable names.
        for name in (
            "jn_current_weather",
            "jn_weather",
            "weather",
            "_weather",
            "mas_current_weather",
            "current_weather",
        ):
            try:
                if hasattr(persistent, name):
                    candidates.append(getattr(persistent, name))
            except Exception:
                pass

        # Optional weather getter functions.
        for name in (
            "get_current_weather",
            "jn_get_current_weather",
            "getWeather",
        ):
            try:
                if hasattr(store, name):
                    func = getattr(store, name)
                    if callable(func):
                        candidates.append(func())
            except Exception:
                pass

        for item in candidates:
            text = jn_wd_to_weather_text(item)

            if not text:
                continue

            if "thunder" in text or "storm" in text or "rain" in text or "shower" in text:
                persistent.jn_weather_drinks_last_weather = "rain"
                return "rain"

            if "snow" in text or "sleet" in text or "blizzard" in text:
                persistent.jn_weather_drinks_last_weather = "snow"
                return "snow"

            if "sun" in text or "clear" in text or "fair" in text:
                persistent.jn_weather_drinks_last_weather = "sunny"
                return "sunny"

            if "cloud" in text or "overcast" in text:
                persistent.jn_weather_drinks_last_weather = "cloudy"
                return "cloudy"

        persistent.jn_weather_drinks_last_weather = "unknown"
        return "unknown"

    def jn_wd_was_done_today(drink_name):
        jn_wd_reset_last_day_if_needed()
        return persistent.jn_weather_drinks_last_day.get(drink_name) == jn_wd_today_key()

    def jn_wd_mark_done_today(drink_name):
        jn_wd_reset_last_day_if_needed()
        persistent.jn_weather_drinks_last_day[drink_name] = jn_wd_today_key()

    def jn_wd_hot_chocolate_condition():
        if not persistent.jn_weather_drinks_enabled:
            return False

        if JN_WD_HOT_CHOCOLATE_ONCE_PER_DAY and jn_wd_was_done_today("hot_chocolate"):
            return False

        return jn_wd_get_weather_text() in ("rain", "snow")

    def jn_wd_milkshake_condition():
        if not persistent.jn_weather_drinks_enabled:
            return False

        if JN_WD_MILKSHAKE_ONCE_PER_DAY and jn_wd_was_done_today("milkshake"):
            return False

        return jn_wd_get_weather_text() == "sunny" and jn_wd_is_daytime()

    def jn_wd_safe_conclude_idle():
        try:
            import store.jn_idles as jn_idles
            jn_idles._concludeIdle()
        except Exception:
            return

    def jn_wd_hide_drinks():
        try:
            renpy.hide("prop", layer="master")
        except Exception:
            pass


# -----------------------------------------------------------------------------
# Image definitions
# -----------------------------------------------------------------------------

image jn_wd_hot_chocolate = Image(JN_WD_HOT_CHOCOLATE_IMAGE_PATH)
image jn_wd_milkshake = Image(JN_WD_MILKSHAKE_IMAGE_PATH)

# Auto-scale/desk placement transform.
# Adjust zoom/xpos/ypos here if your specific test sprites need fine tuning.
transform jn_wd_idle_drink_anim:
    # Anchored to the lower desk plane instead of free-floating screen coordinates.
    # No bobbing/movement. Adjust yoffset only if your desk background differs.
    zoom 0.20
    anchor (0.5, 1.0)
    xalign 0.50
    yalign 1.0
    yoffset -120
    alpha 1.0


# -----------------------------------------------------------------------------
# Idle registration
# -----------------------------------------------------------------------------

init 6 python:
    try:
        import store.jn_affinity as jn_affinity
        import store.jn_idles as jn_idles

        try:
            _jn_wd_idle_type = jn_idles.JNIdleTypes.vibing
        except Exception:
            _jn_wd_idle_type = None

        try:
            jn_idles.__registerIdle(jn_idles.JNIdle(
                label="idle_weather_hot_chocolate",
                idle_type=_jn_wd_idle_type,
                affinity_range=(jn_affinity.NORMAL, None),
                conditional="jn_wd_hot_chocolate_condition()"
            ))
        except Exception as e:
            try:
                store.jn_utils.log("Weather Drinks: could not register hot chocolate idle: {0}".format(e))
            except Exception:
                pass

        try:
            jn_idles.__registerIdle(jn_idles.JNIdle(
                label="idle_weather_milkshake",
                idle_type=_jn_wd_idle_type,
                affinity_range=(jn_affinity.NORMAL, None),
                conditional="jn_wd_milkshake_condition()"
            ))
        except Exception as e:
            try:
                store.jn_utils.log("Weather Drinks: could not register milkshake idle: {0}".format(e))
            except Exception:
                pass

    except Exception as e:
        try:
            store.jn_utils.log("Weather Drinks: idle registration skipped: {0}".format(e))
        except Exception:
            pass


# -----------------------------------------------------------------------------
# Built-in debug button/menu
# -----------------------------------------------------------------------------

screen jn_weather_drinks_debug_button():

    frame:
        xpos 0.98
        ypos 0.02
        anchor (1.0, 0.0)
        background "#00000088"
        padding (6, 4)

        textbutton "Drinks Debug":
            action Show("jn_weather_drinks_debug_menu")


screen jn_weather_drinks_debug_menu():

    tag menu

    frame:
        xpos 0.5
        ypos 0.5
        anchor (0.5, 0.5)
        padding (20, 20)

        vbox:
            spacing 10

            text "Drink Debug Menu" size 30

            textbutton "Hot Chocolate":
                action Jump("idle_weather_hot_chocolate")

            textbutton "Milkshake":
                action Jump("idle_weather_milkshake")

            textbutton "Clear Drink":
                action Jump("jn_weather_drinks_force_clear")

            textbutton "Reset Daily Drink Lock":
                action Jump("jn_weather_drinks_reset_daily_lock")

            textbutton "Close":
                action Hide("jn_weather_drinks_debug_menu")


init 7 python:
    try:
        if "jn_weather_drinks_debug_button" not in config.overlay_screens:
            config.overlay_screens.append("jn_weather_drinks_debug_button")
    except Exception:
        pass


# -----------------------------------------------------------------------------
# Hot chocolate idle
# -----------------------------------------------------------------------------

label idle_weather_hot_chocolate:
    $ jn_wd_mark_done_today("hot_chocolate")

    show black zorder JN_BLACK_ZORDER with Dissolve(0.5)
    show natsuki 1ullbo
    hide black with Dissolve(0.5)

    if persistent.jn_weather_drinks_last_weather == "snow":
        n 1ullbo "...Snow, huh?{w=0.75}{nw}"
        extend 2fcsbg " Yeah, okay.{w=0.5} This calls for something warm."
    else:
        n 1ullbo "...Rain again?{w=0.75}{nw}"
        extend 2fcssm " Hmph.{w=0.5} Then I'm getting something warm."

    n 2fsqsm "And not just plain hot chocolate, either."
    n 2fchbg "Whipped cream and marshmallows.{w=0.5} Obviously."
    n 1uchsm "I'll be right back!"

    show black zorder JN_BLACK_ZORDER with Dissolve(0.5)
    $ jnPause(0.5)
    show jn_wd_hot_chocolate at jn_wd_idle_drink_anim zorder JN_PROP_ZORDER
    show natsuki 1fchsmeme
    play audio drawer
    $ jnPause(1.0)
    hide black with Dissolve(0.5)

    n 1fchbg "There we go!"
    n 2fsqsm "Chocolate, whipped cream, marshmallows...{w=0.5} yep."
    n 2fcssm "Bad weather is way easier to deal with like this."

    show natsuki 1fchsmeme
    $ jnPause(JN_WD_HOT_CHOCOLATE_ENJOY_TIME)

    n 1uchsm "Mmm... okay, that was pretty good."
    n 2fcsss "I guess rain and snow aren't completely terrible when I have something like this."
    n 2fsqsm "I'm putting it away before I start wanting another one."

    show black zorder JN_BLACK_ZORDER with Dissolve(0.5)
    $ jnPause(0.5)
    hide jn_wd_hot_chocolate
    hide prop jn_wd_hot_chocolate
    play audio drawer
    $ jnPause(1.0)
    show natsuki 1fchsmeme
    hide black with Dissolve(0.5)

    n 1unmbo "Okay, I'm back."

    $ jn_wd_safe_conclude_idle()
    return


# -----------------------------------------------------------------------------
# Strawberry and cream milkshake idle
# -----------------------------------------------------------------------------

label idle_weather_milkshake:
    $ jn_wd_mark_done_today("milkshake")

    show black zorder JN_BLACK_ZORDER with Dissolve(0.5)
    show natsuki 1ullbo
    hide black with Dissolve(0.5)

    n 1ullss "It's actually pretty nice out right now."
    n 2fchbg "Sunny weather means I get to have something cold and sweet."
    n 2fsqsm "A strawberry and cream milkshake sounds perfect..."
    n 2fchsm "With just a dash of chocolate, obviously."
    n 1uchbg "I'll grab one really quick!"

    show black zorder JN_BLACK_ZORDER with Dissolve(0.5)
    $ jnPause(0.5)
    show jn_wd_milkshake at jn_wd_idle_drink_anim zorder JN_PROP_ZORDER
    show natsuki 1fchsmeme
    play audio drawer
    $ jnPause(1.0)
    hide black with Dissolve(0.5)

    n 1fchbg "Okay, now this looks good."
    n 2fcssm "Strawberry, cream, and just enough chocolate to make it better."
    n 2fsqsm "Don't get jealous."

    show natsuki 1fchsmeme
    $ jnPause(JN_WD_MILKSHAKE_ENJOY_TIME)

    n 1uchsm "Mmm... that was really good."
    n 2fcsss "Cold, sweet, and not too heavy."
    n 2fsqsm "I'm putting it away before I get brain freeze."

    show black zorder JN_BLACK_ZORDER with Dissolve(0.5)
    $ jnPause(0.5)
    hide jn_wd_milkshake
    hide prop jn_wd_milkshake
    play audio drawer
    $ jnPause(1.0)
    show natsuki 1fchsmeme
    hide black with Dissolve(0.5)

    n 1unmbo "Alright, I'm done."

    $ jn_wd_safe_conclude_idle()
    return


# -----------------------------------------------------------------------------
# Debug/helper labels
# -----------------------------------------------------------------------------

label jn_weather_drinks_force_clear:
    $ jn_wd_reset_last_day_if_needed()
    hide jn_wd_hot_chocolate
    hide prop jn_wd_hot_chocolate
    hide jn_wd_milkshake
    hide prop jn_wd_milkshake
    $ renpy.notify("Drink cleared.")
    return


label jn_weather_drinks_reset_daily_lock:
    $ persistent.jn_weather_drinks_last_day = {}
    $ renpy.notify("Daily drink lock reset.")
    return
