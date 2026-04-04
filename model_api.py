import requests
from execution_engine import ExecutionEngine as EE

# Paste the URL printed in your Colab notebook
API_URL = "https://craft-sally-mph-conditioning.trycloudflare.com/predict"  # Replace with your actual Colab API URL


# The LaTeX equation you want the Colab GPU to analyze
equation = "\\frac{dy}{dx} = 4y^2 e^x"
equation = "(2xy + 3) dx + (x^2 + 4y) dy = 0"
equation = "5\\sin x y + \\frac{dy}{dx} = 2 x^2"
# equation = "2 x y + \\frac{dy}{dx} = x^{2}"
payload = {
    "latex_equation": equation
}

ee = EE()

print("Sending equation to Colab GPU...")
response = requests.post(API_URL, json=payload)

if response.status_code == 200:
    plan = response.json()
    print("✅ Received JSON Plan from Model:")
    print(plan)
    print("==============================================================================================")
    print("\nExecuting the plan using the Execution Engine..., solving ", equation)
    print("==============================================================================================")
    
    ee.prepare_execution(payload["latex_equation"], plan.get("steps", []))
    result = ee.execute()
    print("==============================================================================================")
    print("Final result from execution engine:", result)
    
else:
    print(f"❌ Error {response.status_code}:")
    print(response.text)