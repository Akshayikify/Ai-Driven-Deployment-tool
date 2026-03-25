import { useUser } from "@clerk/clerk-react";
import { useEffect } from "react";

export default function UserSync() {
  const { user, isLoaded, isSignedIn } = useUser();

  useEffect(() => {
    if (isLoaded && isSignedIn && user) {
      const syncUser = async () => {
        try {
          console.log("Syncing user to MongoDB:", user.id);
          const response = await fetch(`http://127.0.0.1:8000/api/v1/auth/sync-user?clerk_id=${user.id}`, {
            method: "POST",
          });
          
          if (!response.ok) {
            console.error("Failed to sync user:", await response.text());
          } else {
            console.log("User synced successfully");
          }
        } catch (error) {
          console.error("Error syncing user:", error);
        }
      };

      syncUser();
    }
  }, [isLoaded, isSignedIn, user]);

  return null;
}
