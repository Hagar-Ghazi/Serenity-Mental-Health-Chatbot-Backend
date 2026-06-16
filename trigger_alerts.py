import time
import sys
import requests

DEFAULT_URL = "https://hagarghazi-serenity-backend.hf.space"


def trigger_error_rate(api_url):
    """Sends rapid requests to trigger the 429 rate limiter, causing a spike in http_errors_total."""
    print("\n--- Triggering High Error Rate Alert ---")
    print(f"Sending 30 rapid requests to {api_url}/chat to exceed rate limits...")

    success_count = 0
    error_count = 0

    for i in range(1, 31):
        try:
            # We send a light request to /chat
            response = requests.post(
                f"{api_url}/chat",
                json={"message": "hi"},
                headers={
                    "X-Forwarded-For": "test-flood-ip"
                },  # Force rate limiting for this IP
                timeout=5,
            )
            if response.status_code == 429:
                error_count += 1
                sys.stdout.write("❌")
            elif response.status_code == 200:
                success_count += 1
                sys.stdout.write("✅")
            else:
                error_count += 1
                sys.stdout.write("⚠️")
            sys.stdout.flush()
        except Exception:
            error_count += 1
            sys.stdout.write("🚨")
            sys.stdout.flush()
        time.sleep(0.05)  # Fast rate

    total = success_count + error_count
    error_rate = (error_count / total) * 100 if total > 0 else 0
    print(f"\nSent {total} requests.")
    print(f"Successes (200 OK): {success_count}")
    print(f"Errors (429/failures): {error_count}")
    print(f"Resulting Error Rate: {error_rate:.1f}% (Threshold is 5.0%)")
    print(
        "\n👉 Axiom check runs every 5 minutes. The monitor should change to 'Triggered' soon."
    )


def recover_normal(api_url):
    """Waits and advises user to stop traffic, letting metrics cool down to 0% errors."""
    print("\n--- Recovering to Normal Case ---")
    print("To return the monitors to a 'Normal' status, we will stop sending requests.")
    print(
        "Since Axiom monitors use a rolling 10-minute window, the error rate will cool down."
    )
    print("Waiting 10 seconds for current request queue to clear...")
    for i in range(10, 0, -1):
        sys.stdout.write(f"\rCooling down... {i}s remaining")
        sys.stdout.flush()
        time.sleep(1)
    print(
        "\n\n✅ Traffic stopped. Let Axiom run its schedule. The monitor status will return to 'Normal' within the next 5-10 minutes."
    )


def main():
    print("==================================================")
    print("   Serenity Chatbot - Axiom Monitor Tester       ")
    print("==================================================")

    api_url = input(f"Enter Backend API URL [{DEFAULT_URL}]: ").strip()
    if not api_url:
        api_url = DEFAULT_URL

    api_url = api_url.rstrip("/")

    # Check health first
    try:
        r = requests.get(f"{api_url}/health", timeout=5)
        if r.status_code == 200:
            print(f"Connected to Backend successfully: {r.json()}")
        else:
            print(f"Warning: Health endpoint returned status {r.status_code}")
    except Exception as e:
        print(f"Error connecting to backend: {e}")
        sys.exit(1)

    print("\nSelect an action:")
    print("1. Trigger High Error Rate Alert (Exceed Rate Limits)")
    print("2. Cool down & Recover to Normal Case")
    print("3. Run both sequentially (Trigger, sleep 5s, then stop)")
    choice = input("Enter choice (1/2/3): ").strip()

    if choice == "1":
        trigger_error_rate(api_url)
    elif choice == "2":
        recover_normal(api_url)
    elif choice == "3":
        trigger_error_rate(api_url)
        print("\nWaiting 5 seconds before initiating cooldown...")
        time.sleep(5)
        recover_normal(api_url)
    else:
        print("Invalid choice.")


if __name__ == "__main__":
    main()
