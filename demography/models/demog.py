from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResDemography(models.Model):
    _name = "demog"
    _description = "Demographic Data"
    _order = "year desc, id desc"

    # Identifiers
    name = fields.Char(string="Name", compute="_compute_name", store=True, index=True)
    year = fields.Integer(string="Year", required=True, index=True)
    source = fields.Char(string="Data Source")
    note = fields.Text(string="Notes")

    # Geographic linkage
    country_id = fields.Many2one(
        "res.country", string="Country", index=True, ondelete="restrict"
    )
    state_id = fields.Many2one(
        "res.country.state",
        string="State",
        domain="[('country_id', '=?', country_id)]",
        ondelete="restrict",
    )
    county_id = fields.Many2one(
        "res.county",
        string="County",
        domain="[('state_id', '=?', state_id)]",
        ondelete="restrict",
    )
    city_id = fields.Many2one(
        "res.city",
        string="City",
        domain="[('county_id', '=?', county_id)]",
        ondelete="restrict",
    )
    city_div_id = fields.Many2one(
        "res.city.div",
        string="City Division",
        domain="[('city_id', '=?', city_id)]",
        ondelete="restrict",
    )
    rural_dist_id = fields.Many2one(
        "res.rural.dist",
        string="Rural District",
        domain="[('county_id', '=?', county_id)]",
        ondelete="restrict",
    )
    rural_dist_div_id = fields.Many2one(
        "res.rural.dist.div",
        string="Rural District Division",
        domain="[('rural_dist_id', '=?', rural_dist_id)]",
        ondelete="restrict",
    )

    # Population
    population_total = fields.Integer(string="Total Population")
    population_density = fields.Float(string="Population Density (per km²)")

    # Age Distribution
    age_0_14 = fields.Float(string="Age 0–14 (%)")
    age_15_24 = fields.Float(string="Age 15–24 (%)")
    age_25_64 = fields.Float(string="Age 25–64 (%)")
    age_65_plus = fields.Float(string="Age 65+ (%)")
    median_age = fields.Float(string="Median Age")

    # Gender
    male_population = fields.Integer(string="Male Population")
    female_population = fields.Integer(string="Female Population")
    sex_ratio = fields.Float(string="Sex Ratio (males per 100 females)")

    # Education
    literacy_rate = fields.Float(string="Literacy Rate (%)")
    primary_education_rate = fields.Float(string="Primary Education Rate (%)")
    secondary_education_rate = fields.Float(string="Secondary Education Rate (%)")
    higher_education_rate = fields.Float(string="Higher Education Rate (%)")

    # Economy
    median_income = fields.Float(string="Median Income")
    per_capita_income = fields.Float(string="Per Capita Income")
    employment_rate = fields.Float(string="Employment Rate (%)")
    unemployment_rate = fields.Float(string="Unemployment Rate (%)")
    poverty_rate = fields.Float(string="Poverty Rate (%)")
    main_industries = fields.Text(string="Main Industries")

    # Households
    total_households = fields.Integer(string="Total Households")
    average_household_size = fields.Float(string="Average Household Size")
    single_parent_households = fields.Integer(string="Single-Parent Households")
    married_couples = fields.Integer(string="Married Couples")

    # Migration & Fertility
    in_migration_rate = fields.Float(string="In-Migration Rate (%)")
    out_migration_rate = fields.Float(string="Out-Migration Rate (%)")
    net_migration = fields.Integer(string="Net Migration")
    birth_rate = fields.Float(string="Birth Rate (per 1000)")
    death_rate = fields.Float(string="Death Rate (per 1000)")

    # Health
    life_expectancy = fields.Float(string="Life Expectancy")
    disability_rate = fields.Float(string="Disability Rate (%)")
    access_to_healthcare = fields.Selection(
        [
            ("low", "Low"),
            ("medium", "Medium"),
            ("high", "High"),
        ],
        string="Access to Healthcare",
    )
    common_health_issues = fields.Text(string="Common Health Issues")

    # Housing
    total_housing_units = fields.Integer(string="Total Housing Units")
    home_ownership_rate = fields.Float(string="Home Ownership Rate (%)")
    rental_rate = fields.Float(string="Rental Rate (%)")
    vacancy_rate = fields.Float(string="Vacancy Rate (%)")

    # Cultural & Social - Fixed Many2many relations with explicit relation tables
    ethnic_group_ids = fields.Many2many(
        "demog.ethnic.group",
        "demography_ethnic_group_rel",
        "demography_id",
        "ethnic_group_id",
        string="Ethnic Groups",
    )
    religion_ids = fields.Many2many(
        "demog.religion",
        "demography_religion_rel",
        "demography_id",
        "religion_id",
        string="Religions",
    )
    languages_spoken_ids = fields.Many2many(
        "res.lang",
        "demography_lang_rel",
        "demography_id",
        "lang_id",
        string="Languages Spoken",
    )

    @api.depends(
        "year",
        "country_id",
        "state_id",
        "county_id",
        "city_id",
        "city_div_id",
        "rural_dist_id",
        "rural_dist_div_id",
    )
    def _compute_name(self):
        for rec in self:
            parts = []
            if rec.rural_dist_div_id:
                parts.append(rec.rural_dist_div_id.name)
            elif rec.rural_dist_id:
                parts.append(rec.rural_dist_id.name)
            elif rec.city_div_id:
                parts.append(rec.city_div_id.name)
            elif rec.city_id:
                parts.append(rec.city_id.name)
            elif rec.county_id:
                parts.append(rec.county_id.name)
            elif rec.state_id:
                parts.append(rec.state_id.name)
            elif rec.country_id:
                parts.append(rec.country_id.name)

            if not parts:
                parts.append(_("Demographic Data"))

            parts.append(str(rec.year))
            rec.name = " / ".join(parts)

    @api.constrains(
        "country_id",
        "state_id",
        "county_id",
        "city_id",
        "city_div_id",
        "rural_dist_id",
        "rural_dist_div_id",
    )
    def _check_geographic_hierarchy(self):
        """Ensure geographic hierarchy makes sense"""
        for rec in self:
            # Check that only one branch of hierarchy is selected (either city or rural)
            if rec.city_id and rec.rural_dist_id:
                raise ValidationError(
                    _("Cannot set both city and rural district in the same record")
                )

            if rec.city_div_id and not rec.city_id:
                raise ValidationError(_("City division requires a city to be selected"))

            if rec.rural_dist_div_id and not rec.rural_dist_id:
                raise ValidationError(
                    _(
                        "Rural district division requires a rural district to be selected"
                    )
                )

            if rec.county_id and not rec.state_id:
                raise ValidationError(_("County requires a state to be selected"))

            if rec.state_id and not rec.country_id:
                raise ValidationError(_("State requires a country to be selected"))

    @api.constrains(
        "age_0_14",
        "age_15_24",
        "age_25_64",
        "age_65_plus",
        "literacy_rate",
        "primary_education_rate",
        "secondary_education_rate",
        "higher_education_rate",
        "employment_rate",
        "unemployment_rate",
        "poverty_rate",
        "disability_rate",
        "home_ownership_rate",
        "rental_rate",
        "vacancy_rate",
    )
    def _check_percentage_values(self):
        for rec in self:
            for field in [
                "age_0_14",
                "age_15_24",
                "age_25_64",
                "age_65_plus",
                "literacy_rate",
                "primary_education_rate",
                "secondary_education_rate",
                "higher_education_rate",
                "employment_rate",
                "unemployment_rate",
                "poverty_rate",
                "disability_rate",
                "home_ownership_rate",
                "rental_rate",
                "vacancy_rate",
            ]:
                value = rec[field]
                if value is not False and (value < 0 or value > 100):
                    raise ValidationError(
                        _("%s must be between 0 and 100") % self._fields[field].string
                    )

    @api.constrains("male_population", "female_population", "population_total")
    def _check_population_consistency(self):
        for rec in self:
            if rec.male_population and rec.female_population and rec.population_total:
                if (
                    rec.male_population + rec.female_population
                ) != rec.population_total:
                    raise ValidationError(
                        _(
                            "Sum of male and female populations must equal total population"
                        )
                    )

    @api.onchange("male_population", "female_population")
    def _onchange_gender_population(self):
        if self.male_population and self.female_population:
            self.population_total = self.male_population + self.female_population
            if self.female_population != 0:
                self.sex_ratio = (self.male_population / self.female_population) * 100
            else:
                self.sex_ratio = 0

    @api.onchange("age_0_14", "age_15_24", "age_25_64", "age_65_plus")
    def _onchange_age_groups(self):
        total = sum(
            [
                self.age_0_14 or 0,
                self.age_15_24 or 0,
                self.age_25_64 or 0,
                self.age_65_plus or 0,
            ]
        )
        if total > 100:
            warning = {
                "title": _("Warning"),
                "message": _("Sum of age groups exceeds 100%"),
            }
            return {"warning": warning}
