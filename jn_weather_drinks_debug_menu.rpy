# jn_weather_drinks_debug_menu.rpy

init -5 python:
    def jn_wd_safe_notify():
        renpy.notify("Drink submod not loaded correctly.")

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

            textbutton "Close":
                action Hide("jn_weather_drinks_debug_menu")


init 5 python:
    if "jn_weather_drinks_debug_button" not in config.overlay_screens:
        config.overlay_screens.append("jn_weather_drinks_debug_button")


label jn_weather_drinks_force_clear:

    $ persistent.jn_weather_drinks_current = "none"
    $ persistent.jn_weather_drinks_end_time = None
    $ renpy.notify("Drink cleared.")

    return