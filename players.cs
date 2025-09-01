namespace ScoutingApi.Models
{
    public class Player
    {
        public int Id { get; set; }
        public string FirstName { get; set; } = "";
        public string LastName { get; set; } = "";
        public string? Nationality { get; set; }
        public string? Position { get; set; }
        public string? Club { get; set; }
    }
}
