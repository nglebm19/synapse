import { useState, useEffect, createContext, useContext } from "react";

interface ProfileData {
  displayName: string;
  username: string;
  email: string;
  bio: string;
  avatarUrl: string;
  huggingfaceToken: string;
}

interface ProfileContextType {
  profileData: ProfileData;
  updateProfile: (data: Partial<ProfileData>) => void;
  updateAvatar: (avatarUrl: string) => void;
}

const ProfileContext = createContext<ProfileContextType | undefined>(undefined);

export const ProfileProvider = ({ children }: { children: React.ReactNode }) => {
  const [profileData, setProfileData] = useState<ProfileData>({
    displayName: "",
    username: "",
    email: "",
    bio: "",
    avatarUrl: "",
    huggingfaceToken: ""
  });

  // Load profile data from localStorage on mount
  useEffect(() => {
    const savedProfile = localStorage.getItem("userProfile");
    if (savedProfile) {
      setProfileData(JSON.parse(savedProfile));
    }
  }, []);

  // Save profile data to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem("userProfile", JSON.stringify(profileData));
  }, [profileData]);

  const updateProfile = (data: Partial<ProfileData>) => {
    setProfileData(prev => ({ ...prev, ...data }));
  };

  const updateAvatar = (avatarUrl: string) => {
    setProfileData(prev => ({ ...prev, avatarUrl }));
  };

  return (
    <ProfileContext.Provider value={{ profileData, updateProfile, updateAvatar }}>
      {children}
    </ProfileContext.Provider>
  );
};

export const useProfile = () => {
  const context = useContext(ProfileContext);
  if (!context) {
    throw new Error("useProfile must be used within a ProfileProvider");
  }
  return context;
};