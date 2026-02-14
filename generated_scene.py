from manim import *

class PhysicsProblem(Scene):
    def construct(self):
        self.camera.background_color = '#0E1117'

        # --- STEP 1: GIVEN DATA ---
        self.add_sound("step1")
        
        # Titles and Static Objects
        title_step1 = Text("चरण १: दी गई जानकारी", font_size=48, color=YELLOW).to_edge(UP * 1.5)
        
        # Draw the floor
        floor = Line(start=LEFT*6, end=RIGHT*6, color=GREY, stroke_width=2).shift(DOWN*1)
        
        # Draw the block
        block = Square(side_length=2, color=BLUE, fill_opacity=0.5).next_to(floor, UP, buff=0)
        mass_label = Text("m = 5 kg", font_size=24, color=WHITE).move_to(block.get_center())
        
        # Animations Step 1
        self.play(Write(title_step1))
        self.play(Create(floor), Create(block), Write(mass_label))
        self.wait(10) # Audio duration wait
        
        # Cleanup Step 1
        self.play(FadeOut(title_step1))
        self.wait(1)

        # --- STEP 2: APPLYING FORCE ---
        self.add_sound("step2")
        
        title_step2 = Text("चरण २: बल (Force) लगाना", font_size=48, color=YELLOW).to_edge(UP * 1.5)
        
        # Draw Force Vector
        force_arrow = Arrow(start=LEFT*2, end=RIGHT*0.5, color=RED, buff=0).next_to(block, LEFT)
        force_label = Text("F = 20 N", font_size=24, color=RED).next_to(force_arrow, UP)
        
        # Animations Step 2
        self.play(Write(title_step2))
        self.play(GrowArrow(force_arrow), Write(force_label))
        self.wait(10) # Audio duration wait
        
        # Cleanup Step 2
        self.play(FadeOut(title_step2))
        self.wait(1)

        # --- STEP 3: FORMULA ---
        self.add_sound("step3")
        
        title_step3 = Text("चरण ३: न्यूटन का दूसरा नियम", font_size=48, color=YELLOW).to_edge(UP * 1.5)
        
        # Formula Text
        formula_text = Text("बल = द्रव्यमान x त्वरण", font_size=36, color=BLUE_B).next_to(block, UP, buff=1.5)
        symbol_formula = Text("F = m x a", font_size=42, color=WHITE).next_to(formula_text, DOWN)
        
        # Animations Step 3
        self.play(Write(title_step3))
        self.play(Write(formula_text))
        self.play(Write(symbol_formula))
        self.wait(10) # Audio duration wait
        
        # Cleanup Step 3
        self.play(FadeOut(title_step3), FadeOut(formula_text))
        self.wait(1)

        # --- STEP 4: CALCULATION ---
        self.add_sound("step4")
        
        title_step4 = Text("चरण ४: गणना (Calculation)", font_size=48, color=YELLOW).to_edge(UP * 1.5)
        
        # Rearranging formula visual
        rearranged = Text("a = F / m", font_size=42, color=WHITE).move_to(symbol_formula.get_center())
        
        # Substitution
        substitution = Text("a = 20 / 5", font_size=42, color=GREEN).next_to(rearranged, DOWN)
        
        # Animations Step 4
        self.play(Write(title_step4))
        self.play(Transform(symbol_formula, rearranged))
        self.play(Write(substitution))
        self.wait(10) # Audio duration wait
        
        # Cleanup Step 4
        self.play(FadeOut(title_step4), FadeOut(symbol_formula))
        self.wait(1)

        # --- STEP 5: RESULT & ANIMATION ---
        self.add_sound("step5")
        
        title_step5 = Text("उत्तर: 4 m/s²", font_size=48, color=GREEN).to_edge(UP * 1.5)
        final_res = Text("a = 4 m/s²", font_size=48, color=GREEN).move_to(substitution.get_center())
        
        # Animations Step 5 - Show Result
        self.play(Write(title_step5))
        self.play(Transform(substitution, final_res))
        self.wait(2)
        
        # Physical Animation of block moving
        # Group everything moving together
        moving_group = VGroup(block, mass_label, force_arrow, force_label)
        
        # Move to right accelerating
        self.play(
            moving_group.animate.shift(RIGHT * 5),
            run_time=4,
            rate_func=linear # Simplified visual acceleration
        )
        
        self.wait(6) # Remaining audio wait
        self.play(FadeOut(moving_group), FadeOut(floor), FadeOut(title_step5), FadeOut(substitution))