from arcade import Sprite, load_texture


class AnimatedSprite():

    """
    New class for Sprite animation. This class aggregates several Sprite objects.
    This class allows to store different animations (e.g. : Idle, Walk, Run, Crouch, Attack, ...),
    and several states a.k.a. directions (e.g. : up, down, top-right, ...).
    The different states are user-defined : technically a state is just an integer value.
    It is up to you to set which value is linked to which state.
    The different animations are also user-defined : technically each animation is described by a name (string).
    It is up to you to give animation names according to your user needs.
    """
    _current_animation_name: str

    # Private methods
    def _prepare_data_struct(self, frame_duration, back_and_forth, loop_counter, filter_color):
        return {
            "sprite":Sprite(),
            "frame_duration": frame_duration,
            "back_and_forth": back_and_forth,
            "counter": loop_counter,
            "color": filter_color,
        }

    def _get_nb_frames(self):
        """
        Private method to get the number of frames for the current animation
        :return: tuple (int, int, int) number of textures, number of frames when back and forth is enabled, number of frames when counter is enabled (and back and forth)
        """
        nb_frames = 0
        nb_frames_baf = 0
        nb_frames_cnt = 0
        if self._current_animation_name in self._anims[self._state]:
            anim_dict = dict(self._anims[self._state][self._current_animation_name])
            nb_frames     = len(anim_dict["sprite"].textures)
            nb_frames_baf = nb_frames
            nb_frames_cnt = nb_frames
            if anim_dict["back_and_forth"]:
                nb_frames_baf += nb_frames - 2
                if nb_frames_baf <= 0:
                    nb_frames_baf = 1
            if anim_dict["counter"] > 0:
                nb_frames_cnt = nb_frames_baf*anim_dict["counter"]

        return (nb_frames, nb_frames_baf, nb_frames_cnt)

    def _get_frame_index(self):
        """
        Private methods to get the current index to display and the percentage of progression for the current animation.
        For infinite animations, the progress value will go from 0 to 1, and then will go back to 0, ...
        :return: tuple(int, float) index of the frame to display, percentage progression
        """
        frame_idx  = 0
        frame_perc = 0

        if self._current_animation_name in self._anims[self._state]:
            anim_dict = self._anims[self._state][self._current_animation_name]

            # Get number of frames
            nb_frames, nb_frames_baf, nb_frames_cnt = self._get_nb_frames()

            # compute absolute frame index according to time
            frame_idx = int(self._elapsed_duration / anim_dict["frame_duration"])
            # update frame index according to loop counter
            if anim_dict["counter"] <= 0:
                # use modulo for infinite loop
                frame_idx = frame_idx % nb_frames_baf
                # Saturate the final index frame (stay on the last frame)
                frame_perc = min(1.0, frame_idx / nb_frames_baf)
            else:
                # Saturate the final index frame (stay on the last frame)
                frame_perc = min(1.0, frame_idx / nb_frames_cnt)
                if frame_idx >= nb_frames_cnt:
                    frame_idx = nb_frames_cnt - 1
                frame_idx  = frame_idx % nb_frames_baf
            # In case of back And Forth
            if frame_idx >= nb_frames:
                frame_idx = nb_frames_baf - frame_idx

        return frame_idx, frame_perc

    # Constructor
    def __init__(self, nb_states=1):
        """
        Constructor method. There is only one parameter that is the number of states that will be stored in this object. \
        By default, there is only one state. But you can set several ones (e.g. : in case of a 4 direction moving character, you set this value to 4) \
        :param nb_states: number of different animation categories. This value cannot be less than 1.
        """

        #call to parent (Sprite)
        super().__init__()

        # parent fields
        self._state  = 0
        self._x     = -100000
        self._y     = -100000
        self._angle = 0
        self._scale = 1

        # animation data structure
        # First a list of dictionnaries, one entry for one state value
        # Each dictionary entry contains the following :
        # - KEY : name of the animation,
        # - VALUE = dict {
        #     + sprite : Sprite()
        #     + frame_duration : float
        #     + back_and_forth : bool
        #     + counter : int
        #    }
        self._anims = []
        if nb_states < 1:
            raise RuntimeError(f"[ERROR] the number of states for this AnimatedSprite instance is less than 1 ! nb_states={nb_states}")
        for i in range(nb_states):
            self._anims.append({})

        # Current animation name
        self._current_animation_name = None
        # Current displayed texture
        self._cur_texture_index = 0
        # Set elapsed duration (used to know if we have to stop the animation)
        self._elapsed_duration = 0
        # Set play/pause flag
        self._playing = True
        # Percentage progression
        self._percent_progression = 0

    def add_animation(self,
                     animation_name: str,
                     filepath: str,
                     nb_frames_x: int,
                     nb_frames_y: int,
                     frame_width: int,
                     frame_height: int,
                     frame_start_index: int = 0,
                     frame_end_index: int = 0,
                     frame_duration: float = 1 / 24,
                     flipped_horizontally: bool = False,
                     flipped_vertically: bool = False,
                     loop_counter: int = 0,
                     back_and_forth: bool = False,
                     filter_color: tuple = (255, 255, 255, 255),
                     animation_state: int = 0,
                     hit_box_algo: str = 'None',
                     ):
        """
        Adds a new animation in the Sprite object. It takes all images from a given SpriteSheet. \
        This Sprite is animated according to the elapsed time and each frame has the same duration. \
        If the animation is the first to be added, it is automatically selected. \
        One important thing is that ALL frames for this animation MUST have the same sizes.
        :param str animation_name: functional name of your animation. This string will be used to select the animation you want to display. \
        If you have several animations (one per animation state), you can give the same name for all of the animations (e.g. 'walk'/'run'/'idle'). \
        This is the pair 'animation_name'+'animation_state' that will be used to select the correct frame to display
        :param str filepath: path to the image file.
        :param int nb_frames_x: number of frames in the input image, along the x-axis
        :param int nb_frames_y: number of frames in the input image, along the y-axis
        :param int frame_width: width for 1 frame in the input image (frame_width*nb_frames_x shall be lesser than or equal to the image width)
        :param int frame_height: height for 1 frame in the input image (frame_height*nb_frames_y shall be lesser than or equal to the image height)
        :param int frame_start_index: index of the first frame of the current animation. Indexes start at 0. \
        Indexes are taken from left to right and from top to bottom. 0 means the top-left frame in the input image.
        :param int frame_end_index: index of the last frame for the current animation. this value cannot exceed (nb_frames_x*nb_frames_y)-1.
        :param float frame_duration: duration of each frame (in seconds).
        :param bool flipped_horizontally: flag to indicate the frames will be horizontally flipped for this animation.
        :param bool flipped_vertically: flag to indicate the frames will be vertically flipped for this animation.
        :param int loop_counter: integer value to tell how many animation loops must be performed before the animation is being stopped. \
        If the value is zero or less, that means the animation will loop forever. When an animation has finished, it remains on the last frame.
        :param bool back_and_forth: flag to indicate if the frames used in this animation (with indexes between frame_start_index and frame_end_index) \
        must be duplicated in the opposite order. It allows a sprite sheet with 5 frames, '1-2-3-4-5', to create an animation like, \
        either '1-2-3-4-5' (flag value = False) \
        or '1-2-3-4-5-4-3-2' (flag value to True).
        :param tuple filter_color: RGBA tuple to be used like a filter layer. All the frames used in this animation will be color-filtered. \
        Each value of the tuple is a [0-255] integer value.
        :param int animation_state: current state for your animated sprite. It will be used in addition with animation_name, \
        in order to select the correct frame to display. Warning : is you call the select_animation() method, and if one pair 'animation_name'+'animation_state'
        is missing in the animation data structure (e.g. you haven't added this animation yet, have forgotten), the previous selected animation will remain selected.
        :param str hit_box_algo same than hit_box_algorithm from the arcade.Sprite class. This value is set to 'None' by default
        :return None
        """

        # Create data structure if not already existing
        if animation_name in self._anims[animation_state]:
            raise RuntimeError(f"AnimatedSprite : {animation_name} is already added to the current object (animation_state={animation_state})")

        my_dict = self._prepare_data_struct(frame_duration,back_and_forth,loop_counter,filter_color)
        my_dict["sprite"].center_x = self._x
        my_dict["sprite"].center_y = self._y

        # Now create all textures and add them into the list
        direction = "forward"
        if frame_start_index > frame_end_index:
            direction = "backward"
        tmpTex = []
        for y in range(nb_frames_y):
            for x in range(nb_frames_x):
                index = x + (y * nb_frames_x)
                # add index only if in range
                index_ok = False
                if direction =="forward" and index >= frame_start_index and index <= frame_end_index:
                        index_ok = True
                elif direction =="backward" and index >= frame_end_index and index <= frame_start_index:
                        index_ok = True
                if index_ok:
                    # create texture
                    tex = load_texture(
                        filepath,
                        x*frame_width, y*frame_height, frame_width, frame_height,
                        flipped_horizontally=flipped_horizontally,
                        flipped_vertically=flipped_vertically,
                        hit_box_algorithm=hit_box_algo)
                    # Store texture in the texture list
                    if direction == "forward":
                        tmpTex.append(tex)
                    else:
                        tmpTex = [tex,] + tmpTex
        # Store texture in the Sprite class
        for tex in tmpTex:
            my_dict["sprite"].append_texture(tex)

        # Set at least the first texture for this sprite
        my_dict["sprite"].set_texture(0)

        # Store this animation
        self._anims[animation_state][animation_name] = my_dict

        # If this animation is the first, select it, and select the first texture, and play
        if self._current_animation_name == None:
            self.select_animation(animation_name, True, True)

    def select_state(self, new_state, rewind=False, running=True):
        """
        This method just changes the animation_state (but does not change the current animation name). \
        E.g. : This is used to change the direction of a top-down 8-direction character.
        :param int new_state: the value of the new animation state
        :param bool rewind: a flag to indicate if the new animation must be rewind or not. By default no rewind is done.
        :param bool runnning: a flag to indicate if the new animation must be played or stopped. By default the animation is played.
        :return: None
        """
        if new_state < 0 or new_state >= len(self._anims):
            raise RuntimeError(f"[ERR] select_state : ({new_state} is not in the range [0-{len(self._anims)-1}])")
        self._state = new_state
        # Rewind and play if requested
        if rewind:
            self.rewind_animation()
        if running:
            self.resume_animation()

    def select_animation(self, animation_name, rewind=False, running=True):
        """
        Select the current animation to display. \
        This method only checks if there is an animation with the given name in the data structure, \
        for the current animation state. \
        If yes, this animation is selected, and the Sprite class textures field is updated. If not, this method does nothing.
        :param str animation_name: just the functional name of the animation to select.
        :param bool rewind: a flag to indicate if the new animation must be rewind or not. By default no rewind is done.
        :param bool runnning: a flag to indicate if the new animation must be played or stopped. By default the animation is played.
        :return: None
        """
        if animation_name in self._anims[self._state]:
            # Select new animation according to state and animation name
            self._current_animation_name = animation_name
            # Set color
            data_struct = dict(self._anims[self._state][animation_name])
            self.color = data_struct["color"]
            # Rewind and play if requested
            if rewind:
                self.rewind_animation()
            if running:
                self.resume_animation()

    def select_frame(self, frame_index):
        """
        This method selects a specific frame in the stored textures.\
        When calling this method, it automatically pauses the animation. \
        e.g. : this method is used for a 'no animation' multi-sprite. \
        This is up to the user to know how many frames have been added to this animation during the creation process.
        :param int frame_index: number of the requested frame.
        :return: None
        """
        self.pause_animation()
        self._cur_texture_index = frame_index
        self._percent_progression = 0
        # Set the textures for the Sprite class
        data_struct = dict(self._anims[self._state][self._current_animation_name])
        data_struct["sprite"].set_texture(self._cur_texture_index)

    def removeAnimation(self, anim_name):
        """
        Tnis method just removes an animation from the data structure. It will remove the animation from ALL the 'states'.
        :param anim_name: functional name of the animation to remove
        :return: None
        """

        # remove animations from the data structure
        for animation_state in range(len(self._anims)):
            if anim_name in self._anims[animation_state]:
                del self._anims[animation_state][anim_name]
        # check if this animation was the current one selected
        # if yes just raise an error in order to notify the developper
        # to onlyremove unused animations
        if anim_name == self._current_animation_name:
            raise RuntimeError(f"[ERR] AnimatedSprite : remove animation only if not used {anim_name}")

    def update_animation(self, delta_time: float = 1/60):
        """
        This method updates the current animation, in order to select the correct frame that should be displayed. \
        This method must be called from the update() method of the current application
        :param delta_time: number of elapsed seconds since the last update() call
        :return: None
        """

        # Increase current elapsed time if playing
        if self._playing:
            self._elapsed_duration += delta_time

            # If the current animation name is not found in the state list, that means
            # the state has been changed after anim selection. So now we do not update anymore.
            # else, just process
            if self._current_animation_name in self._anims[self._state]:
                # Get current frame index
                frame_idx, frame_perc = self._get_frame_index()
                # set current texture index
                self._cur_texture_index = frame_idx
                # Store current percentage
                self._percent_progression = frame_perc
                # Set texture for Sprite class
                data_struct = dict(self._anims[self._state][self._current_animation_name])
                data_struct["sprite"].set_texture(self._cur_texture_index)

        # update position and angle for the current Sprite
        data_struct = dict(self._anims[self._state][self._current_animation_name])
        data_struct["sprite"].center_x = self._x
        data_struct["sprite"].center_y = self._y
        data_struct["sprite"].angle    = self._angle
        data_struct["sprite"].color    = data_struct["color"]
        data_struct["sprite"].scale    = self._scale

    def draw(self):
        """
        This method draws the correct frame, according to the previous 'update_animation' method call. \
        This method must be called from the draw() method of the current application.
        :return:
        """
        data_struct = dict(self._anims[self._state][self._current_animation_name])
        data_struct["sprite"].draw()

    @property
    def center_x(self):
        return self._x
    @property
    def center_y(self):
        return self._y
    @property
    def angle(self):
        return self._angle
    @property
    def scale(self):
        return self._scale

    @property
    def width(self):
        data_struct = dict(self._anims[self._state][self._current_animation_name])
        return data_struct["sprite"].width

    @property
    def height(self):
        data_struct = dict(self._anims[self._state][self._current_animation_name])
        return data_struct["sprite"].height


    @center_x.setter
    def center_x(self, new_x):
        self._x = new_x
    @center_y.setter
    def center_y(self, new_y):
        self._y = new_y
    @angle.setter
    def angle(self, new_ang):
        self._angle = new_ang
    @scale.setter
    def scale(self, new_scale):
        self._scale= new_scale


    def pause_animation(self):
        """
        Pauses the current animation. It does not rewind it.
        :return: None
        """
        self._playing = False

    def resume_animation(self):
        """
        Resumes the current animation. It does not rewind it.
        :return: None
        """
        self._playing = True

    def rewind_animation(self):
        """
        Just rewinds the current animation to the first frame. It does not change the play/stop flag.
        :return: None
        """
        self._elapsed_duration = 0

    def play_animation(self):
        """
        Rewinds and Plays the current animation.
        :return: None
        """
        self.rewind_animation()
        self.resume_animation()

    def stop_animation(self):
        """
        Stops the current animation and rewinds it.
        :return: None
        """
        self.pause_animation()
        self.rewind_animation()

    def get_current_state(self):
        return self._state

    def get_current_animation(self):
        return self._current_animation_name

    def is_finished(self):
        return self._percent_progression >= 1.0

    def get_percent(self):
        return self._percent_progression
        pass
