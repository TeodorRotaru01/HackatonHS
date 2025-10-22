from coordination.coordinator import Coordinator
import json

if __name__ == "__main__":
    coordinator = Coordinator(start_url="https://shop.example.com")

    # Define the ordered voice commands (recorded files)
    commands = [
        "1_login_username.wav",
        "2_login_password.wav",
        "3_click_login.wav",
        "4_search_product.wav",
        "5_add_to_cart.wav",
        "6_checkout.wav"
    ]

    result = coordinator.run_voice_flow(commands)

    print("=== SESSION SUMMARY ===")
    print(json.dumps(result, indent=2))

    coordinator.shutdown()
