
import ActiveCompanies


# Get English company names
comps = ActiveCompanies.active_companies()
english_names = list(comps.Name)

print(english_names)