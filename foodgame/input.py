import collections
import pygame, sys
from pygame.locals import *

from ruamel.yaml import YAML

# None of this code is particularly optimized yet - currently, it relies heavily on strings.
# I can fix that later if we need to but input code usually isn't a bottleneck.

# Order of intitialization is:
# 1. Construct an InputManager.
# 2. Construct your InputContexts and register with your InputManager.
# 3. Register default keybinds
# 4. Call InputManager.ld_config(yaml_file_string)

# @todo TODO: Error handling for basically everything in here. 

## Up / down state for action codes.
class ActionState:
    PRESSED, RELEASED = range(2)

## An InputContext represents the different situations in which one can input. Examples: Game, menu, etc.
# The InputContext translates keypresses into game actions - it makes keys remappable.
# Keys are mapped to an "Action code," a string somewhat like a virtual keycode that refers to an action in gameplay.
# Keys can only be mapped to one action code, but the reverse is not true. 
# Map as many keys to the same action as you want.
class InputContext():

    ## Initializes an InputContext, passing the name as an argument.
    # Example: InputContext("Menu"), InputContext("Game"), InputContext("ChatBar").
    # Naming convention is UpperSnakeCase
    def __init__(self, n, passkeys=False): 
        self.name = n

        # Initialize a dictionary of mappings of keycode to action name
        self.keymap = {}

        # A list of all actions indexed by default key names. Used for creating the keybind config for the first time.
        self.actions_defaults = { "up" : "MoveUp", "right" : "MoveRight", "down" : "MoveDown", "left" : "MoveLeft" }

        # Initialize a list of which action('s buttons) are held down at the moment.
        self.actions_down = []

        # A handy-dandy debug switch.
        self.debug_input = False

        # The passthrough flag. If this is set to true, all keys not registered to actions
        # will be sent along (via a to be determined method) to another class as text -
        # this is the "type in your name" state.
        self.passthrough = passkeys # Defaults to false.

        self.caps = False

    def handle_event(self, event):
        # @todo TODO: Joystick / controller / mouse support.
        if event.type == pygame.KEYDOWN:
            self.handle_keycode(pygame.key.name(event.key), True)
        elif event.type == pygame.KEYUP:
            self.handle_keycode(pygame.key.name(event.key), False)

    ## Called by handle_event and by attach. The meat of the key handing functionality.
    def handle_keycode(self, key, down):
        # Print debug stuff.
        if self.debug_input==True:
            if down == True:
                state_print = "Down"
            elif down == False:
                state_print = "Up"
            print("Key pressed in InputContext: " + key)
            print("Key state is now: " + state_print)
        # Do we have this registered to any action?
        if(key in self.keymap):
            action = self.keymap[key]
            if self.debug_input==True:
                print("Action code " + action + " detected")
            if( down ):
                if not key in self.actions_down:
                    # Start holding key.
                    self.actions_down.append(action)
            elif( up ):
                if key in self.actions_down:
                    # No longer holding key.
                    self.actions_down.remove(action)
        # If we don't have the key but we ARE set up for passthrough, this might be text input.
        elif(self.passthrough):
            # @todo TODO: Code for passing text along to other classes registered with this handler.
            pass

    ## Registers an action code, with its default key(s).
    # Pass a list as a key to bind multiple keys to this action.
    def register_action_defaults(self, act, keys):
        # Make this a single-element list if it's not a list already.
        if type(key) is not list: keys = [ keys ]
        # Register our keybind defaults. 
        for k in key:
            self.actions_defaults[k] = act

    ## Called when this context becomes active.
    def attach(self, current_down=[]):
        for key in current_down:
            self.handle_keycode(key, True);


    ## Called when this context is no longer active.
    def detach(self):
        del self.actions_down[:] # Clear keys-down list.
        self.caps = False



## InputManager is the meta-InputContext. It's a black box you can shove input into and it will work.
# This remaps key-presses into action codes.
# Keys are mapped to an "Action name," somewhat like a virtual keycode that refers to an action in gameplay.
class InputManager():
    def __init__(self, configver="0.01"): 
        # Input debug switch. Copies to contexts.
        self.debug_input = True

        # This variable represents our current context.
        self.context = InputContext("Default")
        self.contexts = { "Default" : self.context }
        # Make sure this propagates.
        self.context.debug_input = self.debug_input

        # A master list of which keys are held down presently.
        # This is kept separate from a context.actions_down, in order to avoid shenanigans.
        self.keys_down = []

        # This is the current version of your keybindings. If the version in the file isn't
        # the same as the version in the class, the file will be wiped and replaced with
        # defaults. 
        self.config_version = configver

    ## Handle an input-related pygame event.
    # InputManager's update function does not handle more complicated events such as "window closed."
    # Please only pass pygame mouse, keyboard, and joystick events to this function 
    def handle_event(self, event):
        if self.debug_input==True:
            if (event.type == pygame.KEYDOWN) or (event.type == pygame.KEYUP):
                print("Key pressed in InputManager: " +  pygame.key.name(event.key))

        # This next bit processes tracking which keys are currently down.
        if (event.type == pygame.KEYDOWN):
            if not (pygame.key.name(event.key) in self.keys_down):
                self.keys_down.append(pygame.key.name(event.key))
        elif (event.type == pygame.KEYUP):
            if pygame.key.name(event.key) in self.keys_down:
                self.keys_down.remove(pygame.key.name(event.key))
        self.context.handle_event(event)

    ## Change the current context to a different one, specified by name.
    def switch_context(self, name):
        if(name in self.contexts):
            self.context.detach()
            self.context = self.contexts[name]
            self.context.attach(self.keys_down)
            self.context.debug_input = self.debug_input

    def register_context(self, ctx):
        if not (ctx.name in self.contexts):
            self.contexts[ctx.name] = ctx

    ## Load mappings from a config string. This loads to ALL contexts.
    # Contexts which are not registered with the InputManager are ignored
    # @todo TODO: Log a warning if mappings are present for a context
    # which is not loaded.
    def ld_config(self, configstring):
        yaml = YAML()

    ## Called when 
    def gen_config(self):