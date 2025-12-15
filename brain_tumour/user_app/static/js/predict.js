symptoms = [
    'itching', 'skin_rash', 'nodal_skin_eruptions', 'continuous_sneezing', 'shivering', 'chills', 'joint_pain',
    'stomach_pain', 'acidity', 'ulcers_on_tongue', 'muscle_wasting', 'vomiting', 'burning_micturition', 'fatigue',
    'weight_gain', 'anxiety', 'cold_hands_and_feets', 'mood_swings', 'weight_loss', 'restlessness', 'lethargy',
    'patches_in_throat', 'irregular_sugar_level', 'cough', 'high_fever', 'sunken_eyes', 'breathlessness',
    'sweating', 'dehydration', 'indigestion', 'headache', 'yellowish_skin', 'dark_urine', 'nausea',
    'loss_of_appetite', 'pain_behind_the_eyes', 'back_pain', 'constipation', 'abdominal_pain', 'diarrhoea',
    'mild_fever', 'yellow_urine', 'yellowing_of_eyes', 'acute_liver_failure', 'fluid_overload', 'swelling_of_stomach',
    'swelled_lymph_nodes', 'malaise', 'blurred_and_distorted_vision', 'phlegm', 'throat_irritation', 'redness_of_eyes',
    'sinus_pressure', 'runny_nose', 'congestion', 'chest_pain', 'weakness_in_limbs', 'fast_heart_rate',
    'pain_during_bowel_movements', 'pain_in_anal_region', 'bloody_stool', 'irritation_in_anus', 'neck_pain',
    'dizziness', 'cramps', 'bruising', 'obesity', 'swollen_legs', 'swollen_blood_vessels', 'puffy_face_and_eyes',
    'enlarged_thyroid', 'brittle_nails', 'swollen_extremeties', 'excessive_hunger', 'extra_marital_contacts',
    'drying_and_tingling_lips', 'slurred_speech', 'knee_pain', 'hip_joint_pain', 'muscle_weakness', 'stiff_neck',
    'swelling_joints', 'movement_stiffness', 'spinning_movements', 'loss_of_balance', 'unsteadiness',
    'weakness_of_one_body_side', 'loss_of_smell', 'bladder_discomfort', 'continuous_feel_of_urine',
    'passage_of_gases', 'internal_itching', 'toxic_look_(typhos)', 'depression', 'irritability', 'muscle_pain',
    'altered_sensorium', 'red_spots_over_body', 'belly_pain', 'abnormal_menstruation', 'watering_from_eyes',
    'increased_appetite', 'polyuria', 'family_history', 'mucoid_sputum', 'rusty_sputum', 'lack_of_concentration',
    'visual_disturbances', 'receiving_blood_transfusion', 'receiving_unsterile_injections', 'coma',
    'stomach_bleeding', 'distention_of_abdomen', 'history_of_alcohol_consumption', 'blood_in_sputum',
    'prominent_veins_on_calf', 'palpitations', 'painful_walking', 'pus_filled_pimples', 'blackheads', 'scurring',
    'skin_peeling', 'silver_like_dusting', 'small_dents_in_nails', 'inflammatory_nails', 'blister', 'red_sore_around_nose',
    'yellow_crust_ooze', 'prognosis', 'skin_rash', 'pus_filled_pimples', 'mood_swings', 'weight_loss', 'fast_heart_rate',
    'excessive_hunger', 'muscle_weakness', 'abnormal_menstruation', 'muscle_wasting', 'patches_in_throat',
    'high_fever', 'extra_marital_contacts', 'yellowish_skin', 'loss_of_appetite', 'abdominal_pain', 'yellowing_of_eyes',
    'chest_pain', 'loss_of_balance', 'lack_of_concentration', 'blurred_and_distorted_vision', 'drying_and_tingling_lips',
    'slurred_speech', 'stiff_neck', 'swelling_joints', 'painful_walking', 'dark_urine', 'yellow_urine',
    'receiving_blood_transfusion', 'receiving_unsterile_injections', 'visual_disturbances', 'burning_micturition',
    'bladder_discomfort', 'foul_smell_of_urine', 'continuous_feel_of_urine', 'irregular_sugar_level',
    'increased_appetite', 'joint_pain', 'skin_peeling', 'small_dents_in_nails', 'inflammatory_nails',
    'swelling_of_stomach', 'distention_of_abdomen', 'history_of_alcohol_consumption', 'fluid_overload',
    'pain_during_bowel_movements', 'pain_in_anal_region', 'bloody_stool', 'irritation_in_anus', 'acute_liver_failure',
    'stomach_bleeding', 'back_pain', 'weakness_in_limbs', 'neck_pain', 'mucoid_sputum', 'mild_fever', 'muscle_pain',
    'family_history', 'continuous_sneezing', 'watering_from_eyes', 'rusty_sputum', 'weight_gain', 'puffy_face_and_eyes',
    'enlarged_thyroid', 'brittle_nails', 'swollen_extremeties', 'swollen_legs', 'prominent_veins_on_calf',
    'stomach_pain', 'spinning_movements', 'sunken_eyes', 'silver_like_dusting', 'swelled_lymph_nodes',
    'blood_in_sputum', 'swollen_blood_vessels', 'toxic_look_(typhos)', 'belly_pain', 'throat_irritation',
    'redness_of_eyes', 'sinus_pressure', 'runny_nose', 'loss_of_smell', 'passage_of_gases', 'cold_hands_and_feets',
    'weakness_of_one_body_side', 'altered_sensorium', 'nodal_skin_eruptions', 'red_sore_around_nose', 'yellow_crust_ooze',
    'ulcers_on_tongue', 'spotting_urination', 'pain_behind_the_eyes', 'red_spots_over_body', 'internal_itching'
]

let selectedSymptoms = [];

// Initialize autocomplete
$("#symptom").autocomplete({
    source: symptoms
});

// Add symptom to the selected symptoms list
$("#add").click(function () {
    const symptom = $("#symptom").val().trim(); // Trim whitespace

    if (symptom && !selectedSymptoms.includes(symptom)) {
        selectedSymptoms.push(symptom);

        // Add to the visible list
        $("#symptoms").append(`
            <li class="symptom-item">
                <button class="remove-symptom" data-symptom="${symptom}">X</button>
                <span class="symptom-name">${symptom}</span>
            </li>
        `);

        // Clear the input field
        $("#symptom").val("");

        // Update the hidden input
        $("#selected_symptoms").val(JSON.stringify(selectedSymptoms));
    } else {
        alert("Symptom is either empty or already added.");
    }
});

// Remove symptom from the list
$(document).on("click", ".remove-symptom", function () {
    const symptom = $(this).data("symptom");

    // Remove from the array
    selectedSymptoms = selectedSymptoms.filter(s => s !== symptom);

    // Remove from the visible list
    $(this).parent().remove();

    // Update the hidden input
    $("#selected_symptoms").val(JSON.stringify(selectedSymptoms));
});
