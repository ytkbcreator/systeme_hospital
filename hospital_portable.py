# Corrected Code for hospital_portable.py

def get_patient_data():
    # Function to get patient data
    return patient_data


def calculate_treatment_cost(treatment):
    # Function to calculate treatment cost
    cost = treatment['cost']
    return cost


def generate_report(patient_data):
    # Function to generate a report
    report = f"Patient Report:\nName: {patient_data['name']}\nAge: {patient_data['age']}\nCost: {calculate_treatment_cost(patient_data['treatment'])}"    
    return report

if __name__ == '__main__':
    patient_data = get_patient_data()
    report = generate_report(patient_data)
    print(report)