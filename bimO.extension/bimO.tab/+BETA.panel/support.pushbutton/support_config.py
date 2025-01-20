"""Request Support tool config"""
#pylint: disable=E0401,C0103
from pyrevit import script, forms
import os

# get the config xml file
output = script.get_output()
config = "config.xml"
defaults = "defaults.xml"

class SupportConfig:
    @staticmethod
    def file_to_xml(file_name):
        return os.path.join(os.path.dirname(__file__), file_name)

    @staticmethod
    def restore_defaults(sourcexml, targetxml):
        """Restores the default settings from the default_settings.xml file."""
        with open(sourcexml, "r") as file:
            data = file.read()
        with open(targetxml, "w") as file:
            file.write(data)

    @staticmethod
    def check_config_xml(file_name):
        """Checks if the config.xml file exists.
        Args:
        file_name (str): The path to the config.xml file.
        Returns:
        bool: True if the config.xml file exists."""
        if os.path.exists(file_name):
            return file_name
        else:
            SupportConfig.restore_defaults("defaults.xml", file_name)
            return file_name

    @staticmethod
    def get_config_xml_path(file_name):
        """Gets the path to the config.xml file.
        Returns:
        str: The path to the config.xml file."""
        config_xml_path = os.path.join(os.path.dirname(__file__), file_name)
        return config_xml_path
    
    @staticmethod
    def write_config_xml(file_name, new_email, new_hashtags):
        """Writes the default email address to the config.xml file."""
        config_xml_path = SupportConfig.get_config_xml_path(file_name)
        with open(config_xml_path, "w") as file:
            file.write(
                "<config>\n")
            file.write(
                "    <email>{}</email>\n".
                format(new_email))
            # write list of hashtags
            file.write("    <hashtags>\n")
            for hashtag in new_hashtags:
                file.write("        <hashtag>{}</hashtag>\n".format(hashtag))
    
    @staticmethod
    def get_default_email():
        """Reads the default email address from the config.xml file.
        Returns:
        str: The default email address."""
        config_xml_path = SupportConfig.get_config_xml_path(SupportConfig.file_to_xml(config))
        with open(config_xml_path, "r") as file:
            for line in file:
                if "<email>" in line:

                    return (
                        line.strip().replace("<email>", "").
                        replace("</email>", ""))
    
    @staticmethod
    def get_hashtags(file_name):
        """Reads the list of hashtags from the config.xml file.
        Returns:
        list: The list of hashtags."""
        config_xml_path = file_name
        with open(config_xml_path, "r") as file:
            hashtags = []
            for line in file:
                # read the hashtags
                if "<hashtag>" in line:
                    hashtag = line.strip().replace("<hashtag>", "").replace("</hashtag>", "")
                    hashtags.append(hashtag)
            return hashtags
   
    @staticmethod
    def check_email_format(email):
        """Checks if the email address is in the correct format.
        Args:
        email (str): The email address.
        Returns:
        bool: True if the email address is in the correct format."""
        if "@" in email and "." in email:
            return True
        return False

if __name__ == "__main__":
    # check if the config.xml file exists
    try:
        SupportConfig.check_config_xml(SupportConfig.file_to_xml(config))
    except:
        SupportConfig.restore_defaults(SupportConfig.file_to_xml(defaults), 
                                       SupportConfig.file_to_xml(config))
    # read the default email address from the config.xml file
    target_email = SupportConfig.get_default_email()
    new_email = forms.ask_for_string(default=target_email, 
                prompt="Enter the email address for support requests:"
                , title="Support Email Address")
    if new_email is None:
        script.exit()
    if SupportConfig.check_email_format(new_email):
        target_email = new_email
        pass
    else:
        forms.alert("Invalid email address format.", exitscript=True)
    # read the list of hashtags from the config.xml file
    def_hashtags = SupportConfig.get_hashtags(SupportConfig.file_to_xml(defaults))
    new_hashtags = forms.SelectFromList.show(def_hashtags,
                                            botton_name="Add Hashtag", 
                                            title="Select Hashtags", 
                                            multiselect=True,
                                            exit_on_close=True)
    if new_hashtags is None:
        script.exit()
    # write the new email address and hashtags to the config.xml file
    SupportConfig.write_config_xml(SupportConfig.file_to_xml(config),
     target_email, new_hashtags)