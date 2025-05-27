import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

st.set_page_config(page_title="Finals Calculator", page_icon="🎓")
st.title(''':mortar_board: Finals Calculator
Coded By Engr. Jacob R. Deonio''')

def get_grade_point_equivalence(score):
    if 99 <= score <= 100:
        return 1.0
    elif 96 <= score <= 98:
        return 1.25
    elif 93 <= score <= 95:
        return 1.5
    elif 90 <= score <= 92:
        return 1.75
    elif 87 <= score <= 89:
        return 2.0
    elif 84 <= score <= 86:
        return 2.25
    elif 81 <= score <= 83:
        return 2.5
    elif 78 <= score <= 80:
        return 2.75
    elif 75 <= score <= 77:
        return 3.0
    else:
        return "Below 75 (Failed or no GPE)"

def reset_all_session_state():
    keys_to_clear = list(st.session_state.keys())
    for key in keys_to_clear:
        del st.session_state[key]
    st.session_state.page = "input_components"
    st.rerun()

# Initialize session state variables
if "grade_components" not in st.session_state:
    st.session_state.grade_components = []
if "component_weights" not in st.session_state:
    st.session_state.component_weights = []
if "edit_index" not in st.session_state:
    st.session_state.edit_index = None
if "reset_inputs" not in st.session_state:
    st.session_state.reset_inputs = False
if "scores" not in st.session_state:
    st.session_state.scores = {}
if "page" not in st.session_state:
    st.session_state.page = "input_components"
if "exempt_conditions" not in st.session_state:
    st.session_state.exempt_conditions = {}
if "min_prefinal" not in st.session_state:
    st.session_state.min_prefinal = ""

# Clear inputs if reset flag is set
if st.session_state.reset_inputs:
    st.session_state.comp_input = ""
    st.session_state.weight_input = None
    st.session_state.reset_inputs = False

if st.session_state.page == "input_components":
    # Input components page
    st.subheader("➕ Add Grade Component")
    col1, col2 = st.columns(2)
    with col1:
        comp_name = st.text_input(
            "Component Name (e.g., Quiz, Exam)",
            value=st.session_state.get("comp_input", ""),
            key="comp_input",
            placeholder="Enter name"
        )
    if "weight_input" not in st.session_state:
        st.session_state.weight_input = None  # ensures blank field
    with col2:
        weight = st.number_input(
            "Grade Equivalent (%)",
            min_value=0.0,
            max_value=100.0,
            step=None,
            format="%.2f",
            value=st.session_state.get("weight_input", None),
            key="weight_input",
            placeholder="Enter weight"
        )

    if st.button("Add Component"):
        if comp_name and weight is not None and weight > 0:
            st.session_state.grade_components.append(comp_name)
            st.session_state.component_weights.append(weight)
            if comp_name not in st.session_state.scores:
                st.session_state.scores[comp_name] = []
            st.session_state.reset_inputs = True
            st.rerun()
        else:
            st.warning("Please enter a valid component name and weight.")

    st.subheader(":clipboard: Your Grade Components")
    for i, (name, wt) in enumerate(zip(st.session_state.grade_components, st.session_state.component_weights)):
        col1, col2, col3 = st.columns([5, 1, 1])
        if st.session_state.edit_index == i:
            with col1:
                new_name = st.text_input("Edit Component Name", value=name, key=f"edit_name_{i}")
                new_weight = st.number_input(
                    "Edit Grade Equivalent (%)",
                    value=wt,
                    min_value=0.0,
                    max_value=100.0,
                    key=f"edit_weight_{i}"
                )
            with col2:
                if st.button("✅", key=f"save_{i}"):
                    old_name = st.session_state.grade_components[i]
                    st.session_state.grade_components[i] = new_name
                    st.session_state.component_weights[i] = new_weight
                    if old_name != new_name:
                        st.session_state.scores[new_name] = st.session_state.scores.pop(old_name, [])
                    st.session_state.edit_index = None
                    st.rerun()
            with col3:
                if st.button("❌", key=f"cancel_{i}"):
                    st.session_state.edit_index = None
                    st.rerun()
        else:
            col1.write(f"{i + 1}. **{name}** — {wt}%")
            with col2:
                if st.button("✏️", key=f"edit_{i}"):
                    st.session_state.edit_index = i
                    st.rerun()
            with col3:
                if st.button("🗑️", key=f"delete_{i}"):
                    comp_to_delete = st.session_state.grade_components.pop(i)
                    st.session_state.component_weights.pop(i)
                    st.session_state.scores.pop(comp_to_delete, None)
                    st.rerun()

    if st.button("Proceed ➡️"):
        total = sum(st.session_state.component_weights)
        if abs(total - 100.0) < 0.01:
            st.session_state.page = "input_scores"
            st.rerun()
        else:
            st.error("The total of all grade equivalents must equal 100%. Please check your inputs.")
    # Add restart button
    if st.button("🔁 Restart"):
        reset_all_session_state()

elif st.session_state.page == "input_scores":
    # Scroll to top
    components.html(
        """
        <script>
            window.parent.document.querySelector("section.main").scrollTo(0, 0);
        </script>
        """,
        height=0,
    )
    st.subheader("📋 Input Scores for Each Component")

    if st.button("⬅️ Back to Components"):
        st.session_state.page = "input_components"
        st.rerun()

    st.markdown("### 🧾 Grade Components Summary")

    summary_df = pd.DataFrame({
        "Component": st.session_state.grade_components,
        "Weight (%)": [round(w, 2) for w in st.session_state.component_weights]
    })
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

    has_negative = False

    for comp, weight in zip(st.session_state.grade_components, st.session_state.component_weights):
        if comp not in st.session_state.scores:
            st.session_state.scores[comp] = []

        with st.expander(f"{comp} Input"):
            scores_list = st.session_state.scores[comp]
            for idx, score in enumerate(scores_list):
                col1, col2, col3, col4 = st.columns([3, 3, 1, 1])

                if st.session_state.get(f"edit_{comp}_{idx}", False) or score.get("raw") is None:
                    raw_key = f"edit_raw_{comp}_{idx}"
                    total_key = f"edit_total_{comp}_{idx}"
                    default_raw = "" if score.get("raw") is None else str(score["raw"])
                    default_total = "" if score.get("total") is None else str(score["total"])

                    with col1:
                        raw_str = st.text_input(
                            f"{comp} {idx + 1}",
                            value=default_raw,
                            key=raw_key,
                            placeholder="Enter your raw score"
                        )
                    with col2:
                        total_str = st.text_input(
                            "",
                            value=default_total,
                            key=total_key,
                            placeholder="Out of"
                        )
                    with col3:
                        if st.button("✅", key=f"save_{comp}_{idx}"):
                            try:
                                raw = float(raw_str)
                                total = float(total_str)
                                if total > 0 and raw >= 0:
                                    st.session_state.scores[comp][idx] = {'raw': raw, 'total': total}
                                    st.session_state[f"edit_{comp}_{idx}"] = False
                                    st.rerun()
                                else:
                                    st.warning("Raw score must be >= 0 and total must be > 0")
                            except ValueError:
                                st.warning("Please enter valid numbers for raw score and total")
                    with col4:
                        if st.button("❌", key=f"cancel_{comp}_{idx}"):
                            if score.get("raw") is None:
                                st.session_state.scores[comp].pop(idx)
                            st.session_state[f"edit_{comp}_{idx}"] = False
                            st.rerun()
                else:
                    col1.write(f"Test {idx+1}: Raw = {score['raw']}, Total = {score['total']}")
                    percent = (score['raw'] / score['total'] * 100) if score['total'] > 0 else 0
                    if score['raw'] < 0 or score['total'] <= 0:
                        has_negative = True
                    col2.write(f"Percentage = {percent:.2f}%")
                    with col3:
                        if st.button("✏️", key=f"edit_btn_{comp}_{idx}"):  # Updated key here
                            st.session_state[f"edit_{comp}_{idx}"] = True
                            st.rerun()
                    with col4:
                        if st.button("🗑️", key=f"delete_{comp}_{idx}"):
                            st.session_state.scores[comp].pop(idx)
                            st.rerun()

            if st.button(f"➕ Add Test Score for {comp}"):
                st.session_state.scores[comp].append({'raw': None, 'total': None})
                st.rerun()

    if st.button("Proceed ➡️", key="proceed_scores"):
        # Check for negative or invalid scores
        has_invalid = False
        for comp_scores in st.session_state.scores.values():
            for s in comp_scores:
                if s['raw'] is None or s['total'] is None or s['raw'] < 0 or s['total'] <= 0:
                    has_invalid = True
                    break
            if has_invalid:
                break

        if has_invalid:
            st.error("Please ensure all scores are non-negative and totals are positive.")
        else:
            st.session_state.page = "set_conditions"
            st.rerun()
    # Add restart button
    if st.button("🔁 Restart"):
        reset_all_session_state()

elif st.session_state.page == "set_conditions":
    # Scroll to top
    components.html(
        """
        <script>
            window.parent.document.querySelector("section.main").scrollTo(0, 0);
        </script>
        """,
        height=0,
    )
    st.subheader("📊 Summary Before Setting Exemption Conditions")

    if st.button("⬅️ Back to Scores"):
        st.session_state.page = "input_scores"
        st.rerun()

    summary_df = pd.DataFrame({
        "Component": st.session_state.grade_components,
        "Weight (%)": [round(w, 2) for w in st.session_state.component_weights]
    })
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

    st.markdown("### 📝 Test Scores Summary")
    for comp in st.session_state.grade_components:
        with st.expander(f"{comp} Test Scores"):
            for idx, s in enumerate(st.session_state.scores.get(comp, [])):
                if s['raw'] is not None and s['total'] is not None:
                    percent = (s['raw'] / s['total']) * 100 if s['total'] > 0 else 0
                    passed = percent >= 60
                    st.write(f"Test {idx+1}: {s['raw']} / {s['total']} = {percent:.2f}% — {'✅ Pass' if passed else '❌ Fail'}")

    st.markdown("### ✅ Exemption Conditions")
    all_answered = True
    for comp in st.session_state.grade_components:
        choice = st.radio(
            f"Do you need to pass ALL {comp} activities to be exempted from the Final Examination?",
            options=["Yes", "No"],
            key=f"exempt_{comp}"
        )
        st.session_state.exempt_conditions[comp] = choice
        if choice not in ["Yes", "No"]:
            all_answered = False

    st.markdown("### 📉 Minimum Required Prefinal Standing")

    st.session_state.min_prefinal = st.text_input(
        "Enter the minimum prefinal standing (%) required to be exempted from the final exam:",
        value=st.session_state.min_prefinal,
        placeholder="e.g. 70"
    )

    if not st.session_state.min_prefinal:
        st.warning("Please enter your required prefinal standing to proceed.")
    elif not st.session_state.min_prefinal.replace('.', '', 1).isdigit() or not (
            0 <= float(st.session_state.min_prefinal) <= 100):
        st.error("Enter a valid percentage between 0 and 100.")
    else:
        all_answered = all_answered and True  # This ensures other radios are answered too

    if all_answered and st.button("Proceed ➡️", key="proceed_conditions"):
        st.session_state.page = "show_results"
        st.rerun()

    # Add restart button
    if st.button("🔁 Restart"):
        reset_all_session_state()

elif st.session_state.page == "show_results":
    # Scroll to top
    components.html(
        """
        <script>
            window.parent.document.querySelector("section.main").scrollTo(0, 0);
        </script>
        """,
        height=0,
    )
    st.subheader("🎉 Exemption Result")

    if st.button("⬅️ Back to Conditions"):
        st.session_state.page = "set_conditions"
        st.rerun()

    total_weight = 0
    total_contribution = 0
    all_pass_all_conditions_met = True
    summary_data = []

    for comp, weight in zip(st.session_state.grade_components, st.session_state.component_weights):
        comp_scores = st.session_state.scores.get(comp, [])
        valid_scores = [s for s in comp_scores if s['raw'] is not None and s['total'] and s['total'] > 0]
        comp_percentages = [(s['raw'] / s['total']) * 100 for s in valid_scores] if valid_scores else []
        avg_score = sum(comp_percentages) / len(comp_percentages) if comp_percentages else 0

        needs_all_pass = st.session_state.exempt_conditions.get(comp) == "Yes"
        if needs_all_pass:
            for p in comp_percentages:
                if p < 60:
                    all_pass_all_conditions_met = False
                    break

        total_weight += weight
        total_contribution += avg_score * (weight / 100)

        tests_summary = []
        for i, s in enumerate(comp_scores):
            if s['raw'] is not None and s['total'] and s['total'] > 0:
                percent = (s['raw'] / s['total']) * 100
                tests_summary.append(
                    f"Test {i + 1}: {s['raw']} / {s['total']} = {percent:.2f}% {'✅ Pass' if percent >= 60 else '❌ Fail'}")
            else:
                tests_summary.append(f"Test {i + 1}: Incomplete scores")

        summary_data.append({
            "Component": comp,
            "Weight (%)": round(weight, 2),
            "Average (%)": round(avg_score, 2),
            "Tests Summary": "\n".join(tests_summary)
        })

    prefinal = round(total_contribution, 2)
    st.markdown(f"### 📊 Your Prefinal Standing: **{prefinal}%**")

    try:
        min_required = float(st.session_state.min_prefinal)
    except:
        min_required = 100

    if prefinal >= min_required and all_pass_all_conditions_met:
        # Override GPE if below 75
        gpe = "3.0" if prefinal < 75 else get_grade_point_equivalence(prefinal)
        st.markdown(f"### 🎯 Grade Point Equivalence (GPE): **{gpe}**")

        st.success("🎓 Congratulations! You are exempted from the final exam!")
        st.success("It's everything you ever want! It's everything you ever need!")
        st.success("And it's here right in front of you!")
        st.success("This is where you wanna be!")
        st.balloons()

        st.markdown("### 🧾 Detailed Scores Summary")
        df_summary = pd.DataFrame(summary_data)
        for idx, row in df_summary.iterrows():
            st.markdown(f"**{row['Component']}** (Weight: {row['Weight (%)']}%)")
            st.markdown(f"- Average: {row['Average (%)']}%")
            st.text(row['Tests Summary'])

        if st.button("🔁 Restart"):
            reset_all_session_state()

    else:
        gpe = get_grade_point_equivalence(prefinal)
        st.markdown(f"### 🎯 Grade Point Equivalence (GPE): **{gpe}**")

        st.error("❌ You are not exempted from the final exam.")
        if prefinal < min_required:
            st.markdown(f"- Your prefinal standing ({prefinal}%) is below the required minimum ({min_required}%).")
        if not all_pass_all_conditions_met:
            st.markdown(f"- You did not pass all required activities with at least 60%.")

        st.markdown("### 🧾 Detailed Scores Summary")
        df_summary = pd.DataFrame(summary_data)
        for idx, row in df_summary.iterrows():
            st.markdown(f"**{row['Component']}** (Weight: {row['Weight (%)']}%)")
            st.markdown(f"- Average: {row['Average (%)']}%")
            st.text(row['Tests Summary'])

        st.markdown("---")
        st.markdown("### ❓ Want to calculate what you need in the final exam?")
        final_exam_weight = st.number_input(
            "Enter the weight (%) of your final exam:",
            min_value=1,
            max_value=100,
            value=30,
            step=1,
            key="final_exam_weight_input"
        )
        st.session_state.final_exam_weight = final_exam_weight

        st.session_state.calculate_for = st.selectbox(
            "Select what you'd like to calculate:",
            ["Score needed to PASS the subject", "Score needed to QUALIFY for removals"]
        )

        if st.button("🧮 Calculate"):
            st.session_state.page = "calculate_final_needed"
            st.rerun()

elif st.session_state.page == "calculate_final_needed":

    # Scroll to top
    components.html(
        """
        <script>
            window.parent.document.querySelector("section.main").scrollTo(0, 0);
        </script>
        """,
        height=0,
    )
    st.subheader("📈 Final Exam Score Needed")

    if st.button("⬅️ Back to Exemption Results"):
        st.session_state.page = "show_results"
        st.rerun()

    # Calculate prefinal (weighted current grade without final exam)
    prefinal = 0
    total_weight = 0
    for comp, weight in zip(st.session_state.grade_components, st.session_state.component_weights):
        comp_scores = st.session_state.scores.get(comp, [])
        valid_scores = [s for s in comp_scores if s['raw'] is not None and s['total'] and s['total'] > 0]
        comp_percentages = [(s['raw'] / s['total']) * 100 for s in valid_scores] if valid_scores else []
        avg_score = sum(comp_percentages) / len(comp_percentages) if comp_percentages else 0
        prefinal += avg_score * (weight / 100)
        total_weight += weight

    prefinal = round(prefinal, 2)

    # Use user input for final exam weight from previous page, fallback if missing
    final_weight = st.session_state.get("final_exam_weight", 30)
    # Just in case input was invalid or 0
    if final_weight <= 0 or final_weight > 100:
        final_weight = 30

    # User selection: pass or qualify
    user_goal = st.session_state.get("calculate_for", "Score needed to PASS the subject")

    if user_goal == "Score needed to PASS the subject":
        target_grade = 60
    else:
        target_grade = 55

    # Calculate weighted current grade
    weighted_current_grade = prefinal * (100 - final_weight) / 100

    # Calculate required score on final exam
    required_final_score = (target_grade - weighted_current_grade) / (final_weight / 100)

    st.markdown(f"### 🧮 Calculation Result")

    st.markdown(f"- 🎯 **Goal:** {user_goal}")
    st.markdown(f"- 📊 **Your Prefinal Standing:** {prefinal}%")
    st.markdown(f"- 🧮 **Final Exam Weight:** {final_weight}%")
    st.markdown(f"- ✅ **Required Final Exam Score:** {required_final_score:.2f}%")

    if required_final_score > 100:
        st.error("⚠️ The required score exceeds 100%. It may not be possible to reach the target.")
        st.markdown("Try to reach out to your instructor or focus on other requirements if possible.")
    elif required_final_score <= 0:
        st.success("🎉 You already passed regardless of the final exam score!")
        st.balloons()
    else:
        st.success("💪 You can do this!")
        st.markdown("Focus your review and aim for that score — you’ve got this!")

    # Add motivation and celebration 🎉
    st.markdown("---")
    st.markdown("### 🌟 **Final Words**")
    st.markdown("""
    > This is the greatest show! Time to prove that you're a winner.
    > You didn't come this far, just to get this far — one more push and you're done!  
    > Best of luck on your finals. Study smart, stay hydrated, and believe in yourself. 💖
    """)
    st.snow()

    # Add restart button
    if st.button("🔁 Restart"):
        reset_all_session_state()