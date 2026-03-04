# --- IMPORTS ---
import csv
import threading
import requests
import math 
import json 
import os   
from io import StringIO
from urllib.parse import quote # For safe URL handling

from kivy.lang import Builder
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.animation import Animation
from kivy.properties import StringProperty, BooleanProperty, NumericProperty, ListProperty, ObjectProperty
from kivy.utils import get_color_from_hex, platform 
from kivy.factory import Factory

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.label import Label

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineAvatarIconListItem
from kivymd.uix.button import MDFlatButton, MDIconButton, MDFillRoundFlatButton

# --- GITHUB CSV URL (Encoded for spaces/brackets) ---
RAW_URL = "https://raw.githubusercontent.com/Imoter2233/synapse_asset/main/data.csv"
CSV_URL = RAW_URL.replace(" ", "%20")

# --- KIVY UI LAYOUT ---
KV = '''
#:import get_color_from_hex kivy.utils.get_color_from_hex

<BadgeLabel@Label>:
    size_hint: None, None
    size: self.texture_size[0] + dp(20), dp(24)
    font_size: '11sp'
    bold: True
    bg_color: 0, 0, 0, 1
    color: 1, 1, 1, 1
    canvas.before:
        Color:
            rgba: self.bg_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(6)]

<DotButton@ButtonBehavior+Label>:
    size_hint: None, None
    size: dp(34), dp(34)
    font_size: '14sp'
    bold: True
    color: app.color_text_inverse if self.text in['T', 'F'] else app.color_text
    halign: 'center'
    valign: 'middle'
    text_size: self.size
    canvas.before:
        Color:
            rgba: self.bg_color if self.text in['T', 'F'] else (0,0,0,0)
        Ellipse:
            pos: self.pos
            size: self.size
        Color:
            rgba: app.color_border if self.text not in['T', 'F'] else (0,0,0,0)
        Line:
            circle: (self.center_x, self.center_y, dp(16))
            width: dp(1.2)

<RootItem>:
    orientation: 'vertical'
    size_hint_y: None
    height: self.minimum_height
    padding:[0, dp(6), 0, dp(6)]
    BoxLayout:
        size_hint_y: None
        height: max(dot_btn.height, root_lbl.texture_size[1])
        spacing: dp(15)
        DotButton:
            id: dot_btn
            text: root.dot_text
            pos_hint: {"top": 1}
            bg_color: app.color_correct if root.dot_text == 'T' else (app.color_wrong if root.dot_text == 'F' else (0,0,0,0))
            on_release: root.handle_dot_click()
        Label:
            id: root_lbl
            text: root.root_text
            color: app.color_text
            font_size: '15sp'
            valign: "top"
            text_size: self.width, None
            size_hint_y: None
            height: self.texture_size[1]
            on_touch_down: if self.collide_point(*args[1].pos): root.toggle_explanation()
    BoxLayout:
        id: exp_container
        size_hint_y: None
        height: dp(0)
        opacity: 0
        padding:[dp(49), dp(5), 0, dp(5)]
        Label:
            id: root_exp_lbl
            text: root.exp_text
            color: app.color_text_sec
            italic: True
            font_size: '13sp'
            valign: "top"
            text_size: self.width, None
            size_hint_y: None
            height: self.texture_size[1]

<QuestionCard>:
    orientation: 'vertical'
    size_hint_y: None
    height: self.minimum_height
    padding: dp(20)
    spacing: dp(16)
    canvas.before:
        Color:
            rgba: app.color_card
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(12)]
        Color:
            rgba: app.color_border
        Line:
            rounded_rectangle: (self.x, self.y, self.width, self.height, dp(12))
            width: dp(0.8)
    BoxLayout:
        size_hint_y: None
        height: dp(24)
        spacing: dp(10)
        BadgeLabel:
            text: root.topic_text
            bg_color: app.color_border
            color: app.color_text
        BadgeLabel:
            text: root.year_text
            bg_color: app.color_accent
            color: app.color_text_inverse  
        Widget: 
    Label:
        text: root.stem_text
        color: app.color_text
        font_size: '17sp'
        bold: True
        valign: "top"
        text_size: self.width, None
        size_hint_y: None
        height: self.texture_size[1]
    BoxLayout:
        id: roots_box
        orientation: 'vertical'
        size_hint_y: None
        height: self.minimum_height
        spacing: dp(5)
    Button:
        id: reveal_btn
        text: "SHOW ANSWERS"
        size_hint_y: None
        height: dp(42) if not app.is_exam else dp(0)
        opacity: 1 if not app.is_exam else 0
        disabled: app.is_exam
        background_normal: ''
        background_color: 0,0,0,0
        color: app.color_text_sec
        font_size: '12sp'
        bold: True
        on_release: root.toggle_reveal_all()
        canvas.before:
            Color:
                rgba: app.color_border
            Line:
                rounded_rectangle: (self.x, self.y, self.width, self.height, dp(8))
                width: dp(1)

<PageButton>:
    size_hint: None, None
    size: dp(36), dp(36)
    font_size: '14sp'
    bold: True
    color: app.color_bg if self.is_active else app.color_text
    canvas.before:
        Color:
            rgba: app.color_accent if self.is_active else (0,0,0,0)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(10)]

<ActiveChip>:
    size_hint: None, None
    height: dp(30)
    width: self.minimum_width
    padding:[dp(12), 0, dp(5), 0]
    spacing: dp(5)
    canvas.before:
        Color:
            rgba: app.color_accent
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius:[dp(15)]
    Label:
        text: root.chip_text
        size_hint_x: None
        width: self.texture_size[0]
        color: app.color_text_inverse
        bold: True
        font_size: '12sp'
    MDIconButton:
        icon: "close"
        theme_text_color: "Custom"
        text_color: app.color_text_inverse
        size_hint: None, None
        size: dp(24), dp(24)
        icon_size: "16sp"
        ripple_scale: 0
        pos_hint: {"center_y": .5}
        on_release: app.remove_filter(root.chip_text)

<TimeColumnItem>:
    size_hint_y: None
    height: dp(50)
    font_size: '22sp'
    bold: True
    color: app.color_accent if self.is_selected else app.color_text_sec
    canvas.before:
        Color:
            rgba: app.color_accent if self.is_selected else (0,0,0,0)
        Line:
            rounded_rectangle: (self.x, self.y, self.width, self.height, dp(8))
            width: dp(1.5)

<ReviewRow>:
    size_hint_y: None
    height: dp(60)
    padding:[dp(10), 0, dp(10), 0]
    spacing: dp(15)
    canvas.before:
        Color:
            rgba: app.color_card
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius:[dp(12)]
        Color:
            rgba: app.color_border
        Line:
            rounded_rectangle: (self.x, self.y, self.width, self.height, dp(12))
            width: dp(0.8)
    MDIconButton:
        icon: root.topic_icon
        theme_text_color: "Custom"
        text_color: root.topic_color
        pos_hint: {"center_y": .5}
        user_font_size: "24sp"
        ripple_scale: 0
    Label:
        text: root.topic_name
        color: app.color_text
        bold: True
        font_size: '16sp'
        text_size: self.size
        halign: 'left'
        valign: 'middle'
    Label:
        text: str(root.topic_score) + "%"
        color: root.topic_color
        bold: True
        font_size: '18sp'
        size_hint_x: None
        width: dp(60)
        text_size: self.size
        halign: 'right'
        valign: 'middle'

<ListItemWithCheckbox>:
    IconRightWidget:
        icon: "check"
        opacity: 1 if root.is_selected else 0

MDScreenManager:
    id: screen_manager
    MDScreen:
        name: "splash_screen"
        canvas.before:
            Color:
                rgba: app.color_bg
            Rectangle:
                pos: self.pos
                size: self.size
        FloatLayout:
            Label:
                text: "[b]SYNAPSE[/b][color=#F59E0B].[/color]"
                markup: True
                font_size: '45sp'
                color: app.color_text
                pos_hint: {"center_x": .5, "center_y": .6}
            BoxLayout:
                size_hint: None, None
                size: dp(100), dp(30)
                pos_hint: {"center_x": .5, "center_y": .45}
                spacing: dp(15)
                Widget:
                    canvas.before:
                        Color:
                            rgba: app.color_accent
                        Ellipse:
                            pos: self.x, self.y + app.dot1_y
                            size: dp(18), dp(18)
                Widget:
                    canvas.before:
                        Color:
                            rgba: app.color_accent
                        Ellipse:
                            pos: self.x, self.y + app.dot2_y
                            size: dp(18), dp(18)
                Widget:
                    canvas.before:
                        Color:
                            rgba: app.color_accent
                        Ellipse:
                            pos: self.x, self.y + app.dot3_y
                            size: dp(18), dp(18)

    MDScreen:
        name: "main_screen"
        MDNavigationLayout:
            MDScreenManager:
                MDScreen:
                    canvas.before:
                        Color:
                            rgba: app.color_bg
                        Rectangle:
                            pos: self.pos
                            size: self.size
                    BoxLayout:
                        orientation: 'vertical'
                        BoxLayout:
                            orientation: 'vertical'
                            size_hint_y: None
                            height: self.minimum_height
                            canvas.before:
                                Color:
                                    rgba: app.color_card
                                Rectangle:
                                    pos: self.pos
                                    size: self.size
                                Color:
                                    rgba: app.color_border
                                Line:
                                    points:[self.x, self.y, self.right, self.y]
                                    width: dp(1)
                            BoxLayout:
                                size_hint_y: None
                                height: dp(65)
                                padding:[dp(5), 0, dp(10), 0]
                                MDIconButton:
                                    icon: "menu"
                                    theme_text_color: "Custom"
                                    text_color: app.color_text
                                    pos_hint: {"center_y": .5}
                                    ripple_scale: 0
                                    on_release: nav_drawer.set_state("open")
                                Label:
                                    text: "[b]SYNAPSE[/b][color=#F59E0B].[/color]"
                                    markup: True
                                    font_size: '20sp'
                                    color: app.color_text
                                    size_hint_x: 1
                                    text_size: self.size
                                    halign: "left"
                                    valign: "center"
                                Label:
                                    on_parent: app.timer_lbl = self
                                    text: "00:00"
                                    color: app.color_wrong
                                    font_size: '22sp'
                                    bold: True
                                    size_hint_x: None
                                    width: dp(75) if app.is_exam else dp(0)
                                    opacity: 1 if app.is_exam else 0
                                MDIconButton:
                                    icon: "tune"
                                    theme_text_color: "Custom"
                                    text_color: app.color_text
                                    pos_hint: {"center_y": .5}
                                    ripple_scale: 0
                                    on_release: app.open_filter_dialog()
                            BoxLayout:
                                size_hint_y: None
                                height: dp(65)
                                padding:[dp(15), dp(10), dp(15), dp(10)]
                                BoxLayout:
                                    canvas.before:
                                        Color:
                                            rgba: app.color_accent if app.search_focused else app.color_border
                                        Line:
                                            rounded_rectangle: (self.x, self.y, self.width, self.height, dp(22.5))
                                            width: dp(1.5) if app.search_focused else dp(1)
                                    padding:[dp(15), 0, dp(15), 0]
                                    MDIconButton:
                                        icon: "magnify"
                                        theme_text_color: "Custom"
                                        text_color: app.color_text_sec
                                        pos_hint: {"center_y": .5}
                                        ripple_scale: 0
                                    TextInput:
                                        id: search_input
                                        hint_text: "Search questions..."
                                        background_color: 0,0,0,0
                                        foreground_color: app.color_text
                                        hint_text_color: app.color_text_sec
                                        multiline: False
                                        cursor_color: app.color_accent
                                        font_size: '15sp'
                                        halign: 'center' 
                                        size_hint_y: None
                                        height: self.minimum_height
                                        pos_hint: {"center_y": .5}
                                        text: app.search_text
                                        on_text: 
                                            app.search_text = self.text
                                            app.filter_feed()
                                        on_focus: app.search_focused = self.focus
                                    Widget:
                                        size_hint_x: None
                                        width: dp(48)
                            ScrollView:
                                size_hint_y: None
                                height: dp(40) if len(app.active_filters) > 0 else dp(0)
                                opacity: 1 if len(app.active_filters) > 0 else 0
                                do_scroll_y: False
                                BoxLayout:
                                    on_parent: app.chips_container = self
                                    orientation: 'horizontal'
                                    size_hint_x: None
                                    width: self.minimum_width
                                    padding:[dp(15), dp(5), dp(15), dp(5)]
                                    spacing: dp(10)
                        ScrollView:
                            id: scroll_view
                            on_parent: app.main_scroll = self
                            BoxLayout:
                                orientation: 'vertical'
                                size_hint_y: None
                                height: self.minimum_height
                                padding:[dp(15), dp(20), dp(15), dp(40)]
                                spacing: dp(20)
                                BoxLayout:
                                    on_parent: app.feed_container = self
                                    orientation: 'vertical'
                                    size_hint_y: None
                                    height: self.minimum_height
                                    spacing: dp(20)
                                BoxLayout:
                                    on_parent: app.pagination_container = self
                                    size_hint_y: None
                                    height: dp(50)
                                    opacity: 0
                                    disabled: True
                                    spacing: dp(10)
                                    padding:[0, dp(10), 0, 0]
                                Button:
                                    id: submit_btn
                                    text: "SUBMIT EXAM"
                                    size_hint_x: 1
                                    background_normal: ''
                                    background_color: 0,0,0,0
                                    color: app.color_text_inverse
                                    font_size: '14sp'
                                    bold: True
                                    opacity: 1 if app.is_exam else 0
                                    disabled: not app.is_exam
                                    size_hint_y: None
                                    height: dp(55) if app.is_exam else dp(0)
                                    on_release: app.grade_exam()
                                    canvas.before:
                                        Color:
                                            rgba: app.color_accent
                                        RoundedRectangle:
                                            pos: self.pos
                                            size: self.size
                                            radius: [dp(10)]
            MDNavigationDrawer:
                id: nav_drawer
                radius: (0, 16, 16, 0)
                md_bg_color: app.color_card
                BoxLayout:
                    orientation: 'vertical'
                    padding:[0, dp(20), 0, 0]
                    spacing: dp(10)
                    Label:
                        text: "MENU"
                        font_size: '14sp'
                        bold: True
                        color: app.color_text_sec
                        text_size: self.size
                        halign: "left"
                        padding_x: dp(20)
                        size_hint_y: None
                        height: dp(30)
                    OneLineAvatarIconListItem:
                        text: "Study Mode"
                        theme_text_color: "Custom"
                        text_color: app.color_text
                        on_release: app.exit_exam(); nav_drawer.set_state("close")
                        ripple_scale: 0
                        IconLeftWidget:
                            icon: "book-open-outline"
                    OneLineAvatarIconListItem:
                        text: "Exam Mode"
                        theme_text_color: "Custom"
                        text_color: app.color_text
                        on_release: app.show_exam_time_dialog(); nav_drawer.set_state("close")
                        ripple_scale: 0
                        IconLeftWidget:
                            icon: "file-document-edit-outline"
                    OneLineAvatarIconListItem:
                        text: "Toggle Theme"
                        theme_text_color: "Custom"
                        text_color: app.color_text
                        on_release: app.toggle_theme(); nav_drawer.set_state("close")
                        ripple_scale: 0
                        IconLeftWidget:
                            icon: "theme-light-dark"
                    Widget: 

    MDScreen:
        name: "result_screen"
        canvas.before:
            Color:
                rgba: app.color_bg
            Rectangle:
                pos: self.pos
                size: self.size
        BoxLayout:
            orientation: 'vertical'
            padding: dp(30)
            spacing: dp(30)
            Label:
                text: "CLINICAL EVALUATION"
                font_size: '20sp'
                bold: True
                color: app.color_text
                size_hint_y: None
                height: dp(50)
            FloatLayout:
                size_hint_y: None
                height: dp(220)
                Widget:
                    id: doughnut_chart
                    pos_hint: {"center_x": .5, "center_y": .5}
                    size_hint: None, None
                    size: dp(150), dp(150)
                    canvas:
                        Color:
                            rgba: app.color_border
                        Line:
                            circle: (self.center_x, self.center_y, dp(70))
                            width: dp(14)
                        Color:
                            rgba: app.color_accent
                        Line:
                            circle: (self.center_x, self.center_y, dp(70), 0, app.score_angle)
                            width: dp(14)
                Label:
                    text: str(app.final_score) + "%"
                    font_size: '38sp'
                    bold: True
                    color: app.color_text
                    pos_hint: {"center_x": .5, "center_y": .5}
            BoxLayout:
                size_hint_y: None
                height: dp(70)
                canvas.before:
                    Color:
                        rgba: app.color_card
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius:[dp(12)]
                padding: dp(15)
                Label:
                    id: advice_lbl
                    text: "BOARD READINESS: High."
                    bold: True
                    color: app.color_text
            Widget: 
            Button:
                text: "REVIEW TOPICS"
                size_hint_x: 1
                height: dp(55)
                size_hint_y: None
                background_normal: ''
                background_color: 0,0,0,0
                color: 1, 1, 1, 1
                bold: True
                on_release: app.open_review_screen()
                canvas.before:
                    Color:
                        rgba: app.color_correct
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [dp(10)]
            Button:
                text: "RETURN TO STUDY"
                size_hint_x: 1
                height: dp(55)
                size_hint_y: None
                background_normal: ''
                background_color: 0,0,0,0
                color: app.color_text_inverse
                bold: True
                on_release: app.exit_exam()
                canvas.before:
                    Color:
                        rgba: app.color_text
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius:[dp(10)]

    MDScreen:
        name: "review_screen"
        canvas.before:
            Color:
                rgba: app.color_bg
            Rectangle:
                pos: self.pos
                size: self.size
        BoxLayout:
            orientation: 'vertical'
            padding: dp(20)
            spacing: dp(20)
            BoxLayout:
                size_hint_y: None
                height: dp(50)
                MDIconButton:
                    icon: "arrow-left"
                    theme_text_color: "Custom"
                    text_color: app.color_text
                    ripple_scale: 0
                    on_release: root.current = "result_screen"
                Label:
                    text: "TOPIC BREAKDOWN"
                    font_size: '20sp'
                    bold: True
                    color: app.color_text
                    text_size: self.size
                    halign: 'left'
                    valign: 'middle'
            ScrollView:
                BoxLayout:
                    on_parent: app.review_container = self
                    orientation: 'vertical'
                    size_hint_y: None
                    height: self.minimum_height
                    spacing: dp(15)
'''

class ListItemWithCheckbox(OneLineAvatarIconListItem):
    is_selected = BooleanProperty(False)
    topic_name = StringProperty("")

class PageButton(ButtonBehavior, Label):
    is_active = BooleanProperty(False)

class ActiveChip(BoxLayout):
    chip_text = StringProperty("")

class TimeColumnItem(ButtonBehavior, Label):
    is_selected = BooleanProperty(False)

class ReviewRow(BoxLayout):
    topic_name = StringProperty("")
    topic_score = NumericProperty(0)
    topic_icon = StringProperty("")
    topic_color = ListProperty([0,0,0,1])

class RootItem(BoxLayout):
    dot_text = StringProperty("•")
    root_text = StringProperty("")
    exp_text = StringProperty("")
    actual_ans = StringProperty("")
    root_id = StringProperty("")
    def handle_dot_click(self):
        app = MDApp.get_running_app()
        if not app.is_exam:
            if self.dot_text == "•":
                self.dot_text = self.actual_ans
                app.study_answers[self.root_id] = True
            else:
                self.dot_text = "•"
                app.study_answers[self.root_id] = False
        else:
            if self.dot_text == "•":
                self.dot_text = "T"
                app.user_answers[self.root_id] = "T"
            elif self.dot_text == "T":
                self.dot_text = "F"
                app.user_answers[self.root_id] = "F"
            else:
                self.dot_text = "•"
                if self.root_id in app.user_answers:
                    del app.user_answers[self.root_id]
    def toggle_explanation(self):
        app = MDApp.get_running_app()
        if app.is_exam: return 
        container = self.ids.exp_container
        if container.height == dp(0):
            anim = Animation(height=self.ids.root_exp_lbl.texture_size[1] + dp(10), opacity=1, duration=0.2)
            anim.start(container)
            app.exp_revealed[self.root_id] = True 
        else:
            anim = Animation(height=dp(0), opacity=0, duration=0.2)
            anim.start(container)
            app.exp_revealed[self.root_id] = False
    def restore_exp_state(self, dt):
        self.ids.exp_container.height = self.ids.root_exp_lbl.texture_size[1] + dp(10)
        self.ids.exp_container.opacity = 1

class QuestionCard(BoxLayout):
    stem_text = StringProperty("")
    topic_text = StringProperty("")
    year_text = StringProperty("")
    card_id = StringProperty("")
    is_revealed = BooleanProperty(False)
    def populate_roots(self, roots_data):
        app = MDApp.get_running_app()
        for r in roots_data:
            item = RootItem(root_id=r['id'], root_text=r['text'], actual_ans=r['ans'], exp_text=r['info'])
            if app.is_exam:
                if r['id'] in app.user_answers: item.dot_text = app.user_answers[r['id']]
            else:
                if app.study_answers.get(r['id']): item.dot_text = r['ans']
            if app.exp_revealed.get(r['id']): Clock.schedule_once(item.restore_exp_state, 0.1)
            self.ids.roots_box.add_widget(item)
    def toggle_reveal_all(self):
        app = MDApp.get_running_app()
        self.is_revealed = not self.is_revealed
        self.ids.reveal_btn.text = "HIDE ANSWERS" if self.is_revealed else "SHOW ANSWERS"
        for child in self.ids.roots_box.children:
            if self.is_revealed:
                child.dot_text = child.actual_ans
                app.study_answers[child.root_id] = True 
            else:
                child.dot_text = "•"
                app.study_answers[child.root_id] = False 

class SynapseApp(MDApp):
    is_exam = BooleanProperty(False)
    score_angle = NumericProperty(0)
    final_score = NumericProperty(0)
    search_focused = BooleanProperty(False)
    search_text = StringProperty("")
    current_page = NumericProperty(1)
    items_per_page = NumericProperty(5) 
    total_pages = NumericProperty(1)
    feed_container = ObjectProperty(None)
    pagination_container = ObjectProperty(None)
    chips_container = ObjectProperty(None)
    main_scroll = ObjectProperty(None)
    review_container = ObjectProperty(None)
    timer_lbl = ObjectProperty(None)
    dot1_y = NumericProperty(0)
    dot2_y = NumericProperty(0)
    dot3_y = NumericProperty(0)
    color_bg = ListProperty([0, 0, 0, 1])
    color_card = ListProperty([0, 0, 0, 1])
    color_border = ListProperty([0, 0, 0, 1])
    color_text = ListProperty([0, 0, 0, 1])
    color_text_sec = ListProperty([0, 0, 0, 1])
    color_text_inverse = ListProperty([0, 0, 0, 1])
    color_accent = ListProperty([0, 0, 0, 1])
    color_correct = ListProperty(get_color_from_hex("#10B981"))
    color_wrong = ListProperty(get_color_from_hex("#EF4444"))
    color_amber = ListProperty(get_color_from_hex("#F59E0B")) 
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.medicalDB =[]
        self.filtered_db = []
        self.active_filters =[]
        self.temp_filters =[]
        self.user_answers = {}    
        self.study_answers = {}   
        self.exp_revealed = {}    
        self.timer_event = None
        self.time_left = 0
        self.filter_dialog_content = None 
        self.time_dialog = None
        self.topic_map_results = {} 
        self.selected_hr = 0
        self.selected_min = 10
        self.defaultDB =[{"id": "0", "subject": "Offline", "topic": "Sync", "year": "2024", "stem": "Database loading...", "roots": []}]

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.update_colors()
        return Builder.load_string(KV)

    def update_colors(self):
        if self.theme_cls.theme_style == "Dark":
            self.color_bg, self.color_card, self.color_border, self.color_text = get_color_from_hex("#000000"), get_color_from_hex("#111827"), get_color_from_hex("#1F2937"), get_color_from_hex("#F9FAFB")
            self.color_text_sec, self.color_text_inverse, self.color_accent = get_color_from_hex("#9CA3AF"), get_color_from_hex("#000000"), get_color_from_hex("#F59E0B")
        else:
            self.color_bg, self.color_card, self.color_border, self.color_text = get_color_from_hex("#F3F4F6"), get_color_from_hex("#FFFFFF"), get_color_from_hex("#E5E7EB"), get_color_from_hex("#111827")
            self.color_text_sec, self.color_text_inverse, self.color_accent = get_color_from_hex("#6B7280"), get_color_from_hex("#FFFFFF"), get_color_from_hex("#3B82F6")

    def on_start(self):
        if platform == 'android':
            try:
                from jnius import autoclass
                from android.runnable import run_on_ui_thread
                @run_on_ui_thread
                def secure_app():
                    PythonActivity = autoclass('org.kivy.android.PythonActivity')
                    WindowManager = autoclass('android.view.WindowManager$LayoutParams')
                    PythonActivity.mActivity.getWindow().addFlags(WindowManager.FLAG_SECURE)
                secure_app()
            except Exception as e: print(f"FLAG_SECURE error: {e}")
        self.animate_loader()
        threading.Thread(target=self.fetch_csv_data).start()

    def animate_loader(self):
        anim1 = Animation(dot1_y=dp(15), duration=0.3, t='out_quad') + Animation(dot1_y=0, duration=0.3, t='in_quad')
        anim2 = Animation(dot2_y=dp(15), duration=0.3, t='out_quad') + Animation(dot2_y=0, duration=0.3, t='in_quad')
        anim3 = Animation(dot3_y=dp(15), duration=0.3, t='out_quad') + Animation(dot3_y=0, duration=0.3, t='in_quad')
        anim1.repeat, anim2.repeat, anim3.repeat = True, True, True
        anim1.start(self)
        Clock.schedule_once(lambda dt: anim2.start(self), 0.15)
        Clock.schedule_once(lambda dt: anim3.start(self), 0.3)

    def get_cache_path(self): return os.path.join(self.user_data_dir, 'synapse_db_cache.json')

    def fetch_csv_data(self):
        cache_path = self.get_cache_path()
        loaded_from_cache = False
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f: self.medicalDB, loaded_from_cache = json.load(f), True
            except: pass
        try:
            response = requests.get(CSV_URL, timeout=10)
            if response.status_code == 200:
                self.parse_csv(response.text)
                try:
                    with open(cache_path, 'w', encoding='utf-8') as f: json.dump(self.medicalDB, f)
                except: pass
            elif not loaded_from_cache: self.medicalDB = self.defaultDB
        except:
            if not loaded_from_cache: self.medicalDB = self.defaultDB
        Clock.schedule_once(lambda dt: self.build_filter_dialog_once())
        Clock.schedule_once(lambda dt: setattr(self.root, 'current', "main_screen"), 1.5)
        Clock.schedule_once(lambda dt: self.apply_search_and_filters(), 1.6)

    def parse_csv(self, csv_text):
        new_db =[]
        reader = csv.DictReader(StringIO(csv_text))
        for row in reader:
            roots =[]
            for i in range(1, 6):
                raw_ans = row.get(f"r{i}_ans", "").strip().upper()
                roots.append({"id": f"{row['id']}_{i}", "text": row.get(f"r{i}_text", ""), "ans": raw_ans[:1] if raw_ans else "", "info": row.get(f"r{i}_info", "")})
            new_db.append({"id": row['id'], "subject": row['subject'], "topic": row['topic'], "year": row['year'], "stem": row['stem'], "roots": roots})
        self.medicalDB = new_db

    def toggle_theme(self):
        self.theme_cls.theme_style = "Dark" if self.theme_cls.theme_style == "Light" else "Light"
        self.update_colors()

    def filter_feed(self, *args):
        self.current_page = 1
        self.apply_search_and_filters()

    def apply_search_and_filters(self):
        query = self.search_text.lower()
        filtered = self.medicalDB
        if self.active_filters: filtered =[item for item in filtered if item['topic'] in self.active_filters]
        if query: filtered =[item for item in filtered if query in item['stem'].lower() or query in item['topic'].lower()]
        self.filtered_db = filtered
        self.render_feed()

    def render_feed(self):
        if not self.feed_container: return 
        self.feed_container.clear_widgets()
        total_items = len(self.filtered_db)
        self.total_pages = math.ceil(total_items / self.items_per_page) if total_items > 0 else 1
        if self.current_page > self.total_pages: self.current_page = self.total_pages
        start_idx = (self.current_page - 1) * self.items_per_page
        for item in self.filtered_db[start_idx : start_idx + self.items_per_page]:
            card = QuestionCard(card_id=str(item['id']), topic_text=item['topic'], year_text=str(item['year']), stem_text=item['stem'])
            card.populate_roots(item['roots'])
            self.feed_container.add_widget(card)
        self.render_pagination_controls()
        if self.main_scroll: self.main_scroll.scroll_y = 1

    def render_pagination_controls(self):
        if not self.pagination_container: return
        container = self.pagination_container
        container.clear_widgets()
        if self.total_pages <= 1:
            container.opacity, container.disabled, container.height = 0, True, 0
            return
        container.opacity, container.disabled, container.height = 1, False, dp(50)
        left_btn = MDIconButton(icon="chevron-left", theme_text_color="Custom", text_color=self.color_text, disabled=self.current_page == 1)
        left_btn.ripple_scale = 0
        left_btn.bind(on_release=lambda x: self.change_page(self.current_page - 1))
        container.add_widget(left_btn)
        scroll = ScrollView(do_scroll_y=False, size_hint_x=1)
        num_box = BoxLayout(orientation='horizontal', size_hint_x=None, spacing=dp(10), padding=[dp(10), 0])
        num_box.bind(minimum_width=num_box.setter('width'))
        for i in range(1, self.total_pages + 1):
            btn = Factory.PageButton(text=str(i), is_active=(i == self.current_page))
            btn.bind(on_release=lambda instance, page=i: self.change_page(page))
            num_box.add_widget(btn)
        scroll.add_widget(num_box)
        container.add_widget(scroll)
        right_btn = MDIconButton(icon="chevron-right", theme_text_color="Custom", text_color=self.color_text, disabled=self.current_page == self.total_pages)
        right_btn.ripple_scale = 0
        right_btn.bind(on_release=lambda x: self.change_page(self.current_page + 1))
        container.add_widget(right_btn)

    def change_page(self, page_num): self.current_page = page_num; self.render_feed()

    def build_filter_dialog_once(self):
        topics = sorted(list(set([item['topic'] for item in self.medicalDB if item['topic']])))
        self.filter_dialog_content = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(300))
        scroll = ScrollView()
        list_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        list_layout.bind(minimum_height=list_layout.setter('height'))
        for t in topics:
            item = ListItemWithCheckbox(text=t, topic_name=t)
            item.bind(on_release=self.toggle_filter_selection)
            list_layout.add_widget(item)
        scroll.add_widget(list_layout)
        self.filter_dialog_content.add_widget(scroll)

    def render_active_chips(self):
        if not self.chips_container: return
        self.chips_container.clear_widgets()
        for f in self.active_filters: self.chips_container.add_widget(ActiveChip(chip_text=f))

    def remove_filter(self, val):
        if val in self.active_filters: self.active_filters.remove(val)
        if val in self.temp_filters: self.temp_filters.remove(val)
        self.update_filter_checkboxes()
        self.render_active_chips()
        self.current_page = 1
        self.apply_search_and_filters()

    def update_filter_checkboxes(self):
        if not self.filter_dialog_content: return
        list_layout = self.filter_dialog_content.children[0].children[0]
        for child in list_layout.children: child.is_selected = child.topic_name in self.active_filters

    def open_filter_dialog(self):
        if not self.filter_dialog_content: self.build_filter_dialog_once()
        self.temp_filters = self.active_filters.copy()
        self.update_filter_checkboxes()
        if not getattr(self, 'filter_md_dialog', None):
            self.filter_md_dialog = MDDialog(title="Select Topics", type="custom", content_cls=self.filter_dialog_content,
                buttons=[MDFlatButton(text="RESET", text_color=self.color_wrong, on_release=self.reset_filters),
                         MDFlatButton(text="APPLY", text_color=self.color_correct, on_release=self.apply_filters)])
        self.filter_md_dialog.open()

    def toggle_filter_selection(self, instance):
        if instance.is_selected: self.temp_filters.remove(instance.topic_name)
        else: self.temp_filters.append(instance.topic_name)
        instance.is_selected = not instance.is_selected

    def reset_filters(self, *args): self.active_filters, self.temp_filters = [], []; self.render_active_chips(); self.current_page = 1; self.apply_search_and_filters(); self.filter_md_dialog.dismiss()
    def apply_filters(self, *args): self.active_filters = self.temp_filters.copy(); self.render_active_chips(); self.current_page = 1; self.apply_search_and_filters(); self.filter_md_dialog.dismiss()

    def show_exam_time_dialog(self):
        content = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(200), spacing=dp(10))
        for label, items, container_attr, setter in [("HR", range(13), "hr_container", self.set_hr), ("MIN", range(0,60,5), "min_container", self.set_min)]:
            box = BoxLayout(orientation='vertical', spacing=dp(5))
            box.add_widget(Label(text=label, bold=True, color=self.color_text_sec, size_hint_y=None, height=dp(30)))
            scroll = ScrollView(do_scroll_x=False)
            container = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(2))
            container.bind(minimum_height=container.setter('height'))
            setattr(self, container_attr, container)
            for i in items:
                btn = Factory.TimeColumnItem(text=f"{i:02d}", is_selected=(i == (self.selected_hr if label=="HR" else self.selected_min)))
                btn.bind(on_release=lambda instance, val=i, s=setter: s(val))
                container.add_widget(btn)
            scroll.add_widget(container); box.add_widget(scroll); content.add_widget(box)
        self.time_dialog = MDDialog(title="EXAM DURATION", type="custom", content_cls=content, buttons=[MDFlatButton(text="START", text_color=self.color_accent, on_release=self.trigger_exam_start)])
        self.time_dialog.open()

    def set_hr(self, val):
        self.selected_hr = val
        for child in self.hr_container.children: child.is_selected = (int(child.text) == val)
    def set_min(self, val):
        self.selected_min = val
        for child in self.min_container.children: child.is_selected = (int(child.text) == val)

    def trigger_exam_start(self, *args):
        total_mins = (self.selected_hr * 60) + self.selected_min
        if total_mins == 0: total_mins = 10 
        if self.time_dialog: self.time_dialog.dismiss()
        self.start_exam(total_mins)

    def start_exam(self, minutes):
        self.is_exam, self.user_answers, self.study_answers, self.exp_revealed = True, {}, {}, {}
        self.time_left = minutes * 60 
        if self.timer_lbl: self.timer_lbl.opacity = 1
        self.current_page = 1; self.apply_search_and_filters()
        if self.timer_event: self.timer_event.cancel()
        self.timer_event = Clock.schedule_interval(self.update_timer, 1)

    def update_timer(self, dt):
        self.time_left -= 1
        m, s = divmod(self.time_left, 60)
        if self.timer_lbl: self.timer_lbl.text = f"{m:02d}:{s:02d}"
        if self.time_left <= 0: self.grade_exam()

    def grade_exam(self):
        if self.timer_event: self.timer_event.cancel()
        correct, total, self.topic_map_results = 0, 0, {}
        for q in self.filtered_db:
            if q['topic'] not in self.topic_map_results: self.topic_map_results[q['topic']] = {'total': 0, 'correct': 0}
            for r in q['roots']:
                total += 1; self.topic_map_results[q['topic']]['total'] += 1
                if self.user_answers.get(r['id']) == r['ans']: correct += 1; self.topic_map_results[q['topic']]['correct'] += 1
        self.final_score = int((correct / total) * 100) if total > 0 else 0
        self.root.current = "result_screen"
        self.root.ids.advice_lbl.text = "BOARD READINESS: High." if self.final_score >= 70 else "REMEDIATION: Required."
        self.score_angle = 0
        Animation(score_angle=(self.final_score / 100) * 360, duration=2.0, t='out_cubic').start(self)

    def open_review_screen(self):
        if not self.review_container: return
        self.root.current = "review_screen"
        self.review_container.clear_widgets()
        for topic, data in self.topic_map_results.items():
            pct = int((data['correct'] / data['total']) * 100) if data['total'] > 0 else 0
            color, icon = (self.color_correct, "check-circle") if pct >= 80 else ((self.color_amber, "alert-circle") if pct >= 50 else (self.color_wrong, "close-circle"))
            self.review_container.add_widget(Factory.ReviewRow(topic_name=topic, topic_score=pct, topic_icon=icon, topic_color=color))

    def exit_exam(self):
        self.is_exam = False
        if self.timer_event: self.timer_event.cancel()
        if self.timer_lbl: self.timer_lbl.opacity = 0
        self.root.current = "main_screen"; self.current_page = 1; self.apply_search_and_filters()

if __name__ == '__main__': SynapseApp().run()
