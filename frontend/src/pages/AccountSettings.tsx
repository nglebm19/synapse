import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Separator } from "@/components/ui/separator";
import { Upload, User, Mail, AtSign, Key } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { useProfile } from "@/hooks/useProfile";
import { useAuth } from "@/hooks/useAuth";
import Header from "@/components/Header";

const AccountSettings = () => {
  const { toast } = useToast();
  const { profileData, updateProfile, updateAvatar } = useProfile();
  const { user } = useAuth();
  const [isEmailEditable, setIsEmailEditable] = useState(false);

  const handleSave = () => {
    toast({
      title: "Settings saved",
      description: "Your account settings have been updated successfully.",
    });
  };

  const handleAvatarUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      // Create a preview URL for the uploaded image
      const previewUrl = URL.createObjectURL(file);
      updateAvatar(previewUrl);
      
      toast({
        title: "Avatar uploaded",
        description: "Your avatar has been updated.",
      });
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <div className="p-6">
        <div className="max-w-4xl mx-auto space-y-6">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Account Settings</h1>
            <p className="text-muted-foreground mt-2">
              Manage your account information and preferences
            </p>
          </div>

          {/* Profile Information */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <User className="h-5 w-5" />
                Profile Information
              </CardTitle>
              <CardDescription>
                Update your personal information and avatar
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Avatar Section */}
              <div className="flex items-center gap-6">
                <Avatar className="h-24 w-24">
                  <AvatarImage src={profileData.avatarUrl} />
                  <AvatarFallback className="text-lg">
                    {profileData.displayName?.charAt(0) || "U"}
                  </AvatarFallback>
                </Avatar>
                <div className="space-y-2">
                  <Label htmlFor="avatar-upload" className="text-sm font-medium">
                    Profile Picture
                  </Label>
                  <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm" asChild>
                      <label htmlFor="avatar-upload" className="cursor-pointer">
                        <Upload className="h-4 w-4 mr-2" />
                        Upload Avatar
                      </label>
                    </Button>
                    <input
                      id="avatar-upload"
                      type="file"
                      accept="image/*"
                      onChange={handleAvatarUpload}
                      className="hidden"
                    />
                  </div>
                  <p className="text-xs text-muted-foreground">
                    JPG, PNG or GIF. Max size 5MB.
                  </p>
                </div>
              </div>

              <Separator />

              {/* Basic Information */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="display-name">Display Name</Label>
                  <Input
                    id="display-name"
                    placeholder="Enter your display name"
                    value={profileData.displayName}
                    onChange={(e) => updateProfile({ displayName: e.target.value })}
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="username" className="flex items-center gap-2">
                    <AtSign className="h-4 w-4" />
                    Username
                  </Label>
                  <Input
                    id="username"
                    placeholder="Choose a unique username"
                    value={profileData.username}
                    onChange={(e) => updateProfile({ username: e.target.value })}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="email" className="flex items-center gap-2">
                  <Mail className="h-4 w-4" />
                  Email Address
                </Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="Enter your email address"
                  value={user?.email || ""}
                  disabled={!isEmailEditable}
                  onChange={(e) => updateProfile({ email: e.target.value })}
                />
                <button
                  type="button"
                  onClick={() => setIsEmailEditable(!isEmailEditable)}
                  className="text-xs text-primary hover:text-primary/80 transition-colors"
                >
                  {isEmailEditable ? "Cancel edit" : "Edit email"}
                </button>
              </div>

              <div className="space-y-2">
                <Label htmlFor="bio">Bio</Label>
                <Textarea
                  id="bio"
                  placeholder="Tell us about yourself..."
                  className="min-h-[100px]"
                  value={profileData.bio}
                  onChange={(e) => updateProfile({ bio: e.target.value })}
                />
              </div>
            </CardContent>
          </Card>

          {/* API Tokens */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Key className="h-5 w-5" />
                API Tokens
              </CardTitle>
              <CardDescription>
                Manage your API tokens for external services
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="huggingface-token">Hugging Face Token</Label>
                <Input
                  id="huggingface-token"
                  type="password"
                  placeholder="Enter your Hugging Face API token"
                  value={profileData.huggingfaceToken}
                  onChange={(e) => updateProfile({ huggingfaceToken: e.target.value })}
                />
                <p className="text-xs text-muted-foreground">
                  Your token is encrypted and stored securely. It's used for accessing Hugging Face models.
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Save Button */}
          <div className="flex justify-end">
            <Button onClick={handleSave} className="px-8">
              Save Changes
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AccountSettings;