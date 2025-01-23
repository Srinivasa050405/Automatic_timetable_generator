import streamlit as st
import random
from tabulate import tabulate
import pandas as pd

def generate_timetable(subjects, periods_per_subject, num_sections, num_periods, num_days=5):
    timetable = {
        f"Section {i + 1}": {f"Day {j + 1}": [[] for _ in range(num_periods)] for j in range(num_days)}
        for i in range(num_sections)
    }
    
    subject_count = {section: {subject: 0 for subject in subjects} for section in timetable}
    
    # Calculate total required periods per section
    total_required_periods = sum(periods_per_subject)
    total_available_periods = num_days * num_periods
    free_periods_needed = total_available_periods - total_required_periods
    
    # Pre-allocate free periods randomly
    for section in timetable:
        free_slots = []
        for day in range(num_days):
            for period in range(num_periods):
                free_slots.append((day, period))
        
        selected_free_slots = random.sample(free_slots, free_periods_needed)
        for day, period in selected_free_slots:
            timetable[section][f"Day {day + 1}"][period].append("Free")
    
    # Fill in the remaining slots with subjects
    for day in range(num_days):
        for period in range(num_periods):
            used_subjects = set()
            
            for section in timetable:
                if timetable[section][f"Day {day + 1}"][period]:
                    continue
                
                available_subjects = [
                    subject for subject in subjects
                    if subject_count[section][subject] < periods_per_subject[subjects.index(subject)]
                ]
                
                random.shuffle(available_subjects)
                
                assigned = False
                for subject in available_subjects:
                    if subject not in used_subjects:
                        timetable[section][f"Day {day + 1}"][period].append(subject)
                        used_subjects.add(subject)
                        subject_count[section][subject] += 1
                        assigned = True
                        break
                
                if not assigned and not timetable[section][f"Day {day + 1}"][period]:
                    timetable[section][f"Day {day + 1}"][period].append("Free")
    
    return timetable

def convert_timetable_to_df(timetable, section, num_periods):
    data = []
    for period in range(num_periods):
        row = {'Period': f'Period {period + 1}'}
        for day in range(1, 6):
            row[f'Day {day}'] = ', '.join(timetable[section][f'Day {day}'][period])
        data.append(row)
    return pd.DataFrame(data)

def main():
    st.title("School Timetable Generator")
    
    with st.sidebar:
        st.header("Input Parameters")
        num_subjects = st.number_input("Number of Subjects", min_value=1, max_value=10, value=3)
        
        subjects = []
        periods_per_subject = []
        
        # Create two columns for subject inputs
        col1, col2 = st.columns(2)
        
        for i in range(num_subjects):
            with col1:
                subject = st.text_input(f"Subject {i + 1}", value=f"Subject {i + 1}")
                subjects.append(subject)
            
            with col2:
                periods = st.number_input(f"Periods for {subject}", min_value=1, max_value=10, value=4)
                periods_per_subject.append(periods)
        
        num_sections = st.number_input("Number of Sections", min_value=1, max_value=5, value=2)
        num_periods = st.number_input("Periods per Day", min_value=1, max_value=10, value=6)
    
    if st.button("Generate Timetable", type="primary"):
        try:
            timetable = generate_timetable(subjects, periods_per_subject, num_sections, num_periods)
            
            st.success("Timetable generated successfully!")
            
            # Create tabs for each section
            tabs = st.tabs([f"Section {i+1}" for i in range(num_sections)])
            
            for i, tab in enumerate(tabs):
                with tab:
                    section = f"Section {i + 1}"
                    
                    # Count free periods
                    free_count = sum(
                        1 for day in range(1, 6)
                        for period in range(num_periods)
                        if "Free" in timetable[section][f"Day {day}"][period]
                    )
                    
                    st.info(f"Number of free periods: {free_count}")
                    
                    # Convert timetable to DataFrame for better display
                    df = convert_timetable_to_df(timetable, section, num_periods)
                    st.dataframe(df, use_container_width=True)
                    
                    # Add download button for each section
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label=f"Download {section} Timetable",
                        data=csv,
                        file_name=f'timetable_{section.lower().replace(" ", "_")}.csv',
                        mime='text/csv'
                    )
                    
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    st.set_page_config(
        page_title="School Timetable Generator",
        page_icon="📚",
        layout="wide"
    )
    main()
