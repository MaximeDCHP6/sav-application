class AlderError(Exception):
    """Classe de base pour les erreurs de l'application."""
    
    def __init__(self, message: str, code: str = None):
        """Initialise l'erreur.
        
        Args:
            message: Message d'erreur
            code: Code d'erreur (optionnel)
        """
        self.message = message
        self.code = code
        super().__init__(self.message)

class DatabaseError(AlderError):
    """Erreur liée à la base de données."""
    pass

class AuthenticationError(AlderError):
    """Erreur d'authentification."""
    pass

class AuthorizationError(AlderError):
    """Erreur d'autorisation."""
    pass

class ValidationError(AlderError):
    """Erreur de validation des données."""
    pass

class ConfigurationError(AlderError):
    """Erreur de configuration."""
    pass

class ExportError(AlderError):
    """Erreur lors de l'export de données."""
    pass

class ImportError(AlderError):
    """Erreur lors de l'import de données."""
    pass

class BackupError(AlderError):
    """Erreur lors de la sauvegarde."""
    pass

class RestoreError(AlderError):
    """Erreur lors de la restauration."""
    pass

class NotificationError(AlderError):
    """Erreur lors de l'envoi de notification."""
    pass

class DocumentError(AlderError):
    """Erreur liée aux documents."""
    pass

class ReportError(AlderError):
    """Erreur lors de la génération de rapport."""
    pass

class SchedulerError(AlderError):
    """Erreur du planificateur de tâches."""
    pass

class ClientError(AlderError):
    """Erreur liée aux clients."""
    pass

class FRPError(AlderError):
    """Erreur liée aux FRP."""
    pass

class SupplierError(AlderError):
    """Erreur liée aux fournisseurs."""
    pass

class CarrierError(AlderError):
    """Erreur liée aux transporteurs."""
    pass

class UIError(AlderError):
    """Erreur liée à l'interface utilisateur."""
    pass

class NetworkError(AlderError):
    """Erreur réseau."""
    pass

class FileError(AlderError):
    """Erreur liée aux fichiers."""
    pass

class ArchiveError(AlderError):
    """Erreur lors de l'archivage."""
    pass

class StatisticsError(AlderError):
    """Erreur lors du calcul des statistiques."""
    pass

class LogError(AlderError):
    """Erreur liée aux logs."""
    pass

class SecurityError(AlderError):
    """Erreur de sécurité."""
    pass

class ResourceError(AlderError):
    """Erreur liée aux ressources."""
    pass

class TemplateError(AlderError):
    """Erreur liée aux templates."""
    pass

class EmailError(AlderError):
    """Erreur lors de l'envoi d'email."""
    pass

class QRCodeError(AlderError):
    """Erreur lors de la génération de QR code."""
    pass

class BarcodeError(AlderError):
    """Erreur lors de la génération de code-barres."""
    pass

class PDFError(AlderError):
    """Erreur lors de la génération de PDF."""
    pass

class ExcelError(AlderError):
    """Erreur lors de la génération d'Excel."""
    pass

class ImageError(AlderError):
    """Erreur liée aux images."""
    pass

class CacheError(AlderError):
    """Erreur liée au cache."""
    pass

class SessionError(AlderError):
    """Erreur liée aux sessions."""
    pass

class MemoryError(AlderError):
    """Erreur de mémoire."""
    pass

class TimeoutError(AlderError):
    """Erreur de timeout."""
    pass

class ConcurrencyError(AlderError):
    """Erreur de concurrence."""
    pass

class StateError(AlderError):
    """Erreur d'état."""
    pass

class VersionError(AlderError):
    """Erreur de version."""
    pass

class DependencyError(AlderError):
    """Erreur de dépendance."""
    pass

class PluginError(AlderError):
    """Erreur de plugin."""
    pass

class UpdateError(AlderError):
    """Erreur lors de la mise à jour."""
    pass

class MigrationError(AlderError):
    """Erreur lors de la migration."""
    pass

class CleanupError(AlderError):
    """Erreur lors du nettoyage."""
    pass

class MaintenanceError(AlderError):
    """Erreur lors de la maintenance."""
    pass

class SystemError(AlderError):
    """Erreur système."""
    pass

class HardwareError(AlderError):
    """Erreur matérielle."""
    pass

class SoftwareError(AlderError):
    """Erreur logicielle."""
    pass

class IntegrationError(AlderError):
    """Erreur d'intégration."""
    pass

class APIError(AlderError):
    """Erreur d'API."""
    pass

class ServiceError(AlderError):
    """Erreur de service."""
    pass

class ComponentError(AlderError):
    """Erreur de composant."""
    pass

class ModuleError(AlderError):
    """Erreur de module."""
    pass

class PackageError(AlderError):
    """Erreur de package."""
    pass

class LibraryError(AlderError):
    """Erreur de bibliothèque."""
    pass

class FrameworkError(AlderError):
    """Erreur de framework."""
    pass

class PlatformError(AlderError):
    """Erreur de plateforme."""
    pass

class EnvironmentError(AlderError):
    """Erreur d'environnement."""
    pass

class RuntimeError(AlderError):
    """Erreur d'exécution."""
    pass

class CompilationError(AlderError):
    """Erreur de compilation."""
    pass

class SyntaxError(AlderError):
    """Erreur de syntaxe."""
    pass

class SemanticError(AlderError):
    """Erreur sémantique."""
    pass

class LogicError(AlderError):
    """Erreur de logique."""
    pass

class AlgorithmError(AlderError):
    """Erreur d'algorithme."""
    pass

class DataError(AlderError):
    """Erreur de données."""
    pass

class FormatError(AlderError):
    """Erreur de format."""
    pass

class EncodingError(AlderError):
    """Erreur d'encodage."""
    pass

class DecodingError(AlderError):
    """Erreur de décodage."""
    pass

class ParsingError(AlderError):
    """Erreur de parsing."""
    pass

class SerializationError(AlderError):
    """Erreur de sérialisation."""
    pass

class DeserializationError(AlderError):
    """Erreur de désérialisation."""
    pass

class MarshallingError(AlderError):
    """Erreur de marshalling."""
    pass

class UnmarshallingError(AlderError):
    """Erreur de unmarshalling."""
    pass

class ConversionError(AlderError):
    """Erreur de conversion."""
    pass

class TransformationError(AlderError):
    """Erreur de transformation."""
    pass

class MappingError(AlderError):
    """Erreur de mapping."""
    pass

class BindingError(AlderError):
    """Erreur de binding."""
    pass

class ConnectionError(AlderError):
    """Erreur de connexion."""
    pass

class CommunicationError(AlderError):
    """Erreur de communication."""
    pass

class ProtocolError(AlderError):
    """Erreur de protocole."""
    pass

class TransportError(AlderError):
    """Erreur de transport."""
    pass

class RoutingError(AlderError):
    """Erreur de routage."""
    pass

class AddressingError(AlderError):
    """Erreur d'adressage."""
    pass

class NamingError(AlderError):
    """Erreur de nommage."""
    pass

class ResolutionError(AlderError):
    """Erreur de résolution."""
    pass

class DiscoveryError(AlderError):
    """Erreur de découverte."""
    pass

class RegistrationError(AlderError):
    """Erreur d'enregistrement."""
    pass

class DeregistrationError(AlderError):
    """Erreur de désenregistrement."""
    pass

class SubscriptionError(AlderError):
    """Erreur d'abonnement."""
    pass

class UnsubscriptionError(AlderError):
    """Erreur de désabonnement."""
    pass

class PublicationError(AlderError):
    """Erreur de publication."""
    pass

class NotificationError(AlderError):
    """Erreur de notification."""
    pass

class EventError(AlderError):
    """Erreur d'événement."""
    pass

class MessageError(AlderError):
    """Erreur de message."""
    pass

class QueueError(AlderError):
    """Erreur de file d'attente."""
    pass

class StackError(AlderError):
    """Erreur de pile."""
    pass

class BufferError(AlderError):
    """Erreur de buffer."""
    pass

class StreamError(AlderError):
    """Erreur de flux."""
    pass

class ChannelError(AlderError):
    """Erreur de canal."""
    pass

class PortError(AlderError):
    """Erreur de port."""
    pass

class SocketError(AlderError):
    """Erreur de socket."""
    pass

class PipeError(AlderError):
    """Erreur de pipe."""
    pass

class SignalError(AlderError):
    """Erreur de signal."""
    pass

class InterruptError(AlderError):
    """Erreur d'interruption."""
    pass

class DeadlineError(AlderError):
    """Erreur de deadline."""
    pass

class ScheduleError(AlderError):
    """Erreur de planification."""
    pass

class TimingError(AlderError):
    """Erreur de timing."""
    pass

class SynchronizationError(AlderError):
    """Erreur de synchronisation."""
    pass

class CoordinationError(AlderError):
    """Erreur de coordination."""
    pass

class OrchestrationError(AlderError):
    """Erreur d'orchestration."""
    pass

class ChoreographyError(AlderError):
    """Erreur de chorégraphie."""
    pass

class WorkflowError(AlderError):
    """Erreur de workflow."""
    pass

class ProcessError(AlderError):
    """Erreur de processus."""
    pass

class ThreadError(AlderError):
    """Erreur de thread."""
    pass

class TaskError(AlderError):
    """Erreur de tâche."""
    pass

class JobError(AlderError):
    """Erreur de job."""
    pass

class BatchError(AlderError):
    """Erreur de batch."""
    pass

class TransactionError(AlderError):
    """Erreur de transaction."""
    pass

class OperationError(AlderError):
    """Erreur d'opération."""
    pass

class ActionError(AlderError):
    """Erreur d'action."""
    pass

class CommandError(AlderError):
    """Erreur de commande."""
    pass

class QueryError(AlderError):
    """Erreur de requête."""
    pass

class StatementError(AlderError):
    """Erreur de statement."""
    pass

class ExpressionError(AlderError):
    """Erreur d'expression."""
    pass

class FunctionError(AlderError):
    """Erreur de fonction."""
    pass

class MethodError(AlderError):
    """Erreur de méthode."""
    pass

class ProcedureError(AlderError):
    """Erreur de procédure."""
    pass

class RoutineError(AlderError):
    """Erreur de routine."""
    pass

class ScriptError(AlderError):
    """Erreur de script."""
    pass

class ProgramError(AlderError):
    """Erreur de programme."""
    pass

class ApplicationError(AlderError):
    """Erreur d'application."""
    pass

class SystemError(AlderError):
    """Erreur système."""
    pass

class PlatformError(AlderError):
    """Erreur de plateforme."""
    pass

class EnvironmentError(AlderError):
    """Erreur d'environnement."""
    pass

class ConfigurationError(AlderError):
    """Erreur de configuration."""
    pass

class SettingsError(AlderError):
    """Erreur de paramètres."""
    pass

class OptionsError(AlderError):
    """Erreur d'options."""
    pass

class PreferencesError(AlderError):
    """Erreur de préférences."""
    pass

class ProfileError(AlderError):
    """Erreur de profil."""
    pass

class ContextError(AlderError):
    """Erreur de contexte."""
    pass

class StatusError(AlderError):
    """Erreur de statut."""
    pass

class ConditionError(AlderError):
    """Erreur de condition."""
    pass

class ConstraintError(AlderError):
    """Erreur de contrainte."""
    pass

class RequirementError(AlderError):
    """Erreur de requirement."""
    pass

class RelationshipError(AlderError):
    """Erreur de relation."""
    pass

class AssociationError(AlderError):
    """Erreur d'association."""
    pass

class CompositionError(AlderError):
    """Erreur de composition."""
    pass

class AggregationError(AlderError):
    """Erreur d'agrégation."""
    pass

class InheritanceError(AlderError):
    """Erreur d'héritage."""
    pass

class PolymorphismError(AlderError):
    """Erreur de polymorphisme."""
    pass

class EncapsulationError(AlderError):
    """Erreur d'encapsulation."""
    pass

class AbstractionError(AlderError):
    """Erreur d'abstraction."""
    pass

class InterfaceError(AlderError):
    """Erreur d'interface."""
    pass

class ImplementationError(AlderError):
    """Erreur d'implémentation."""
    pass

class DesignError(AlderError):
    """Erreur de design."""
    pass

class ArchitectureError(AlderError):
    """Erreur d'architecture."""
    pass

class StructureError(AlderError):
    """Erreur de structure."""
    pass

class OrganizationError(AlderError):
    """Erreur d'organisation."""
    pass

class LayoutError(AlderError):
    """Erreur de layout."""
    pass

class FormattingError(AlderError):
    """Erreur de formatage."""
    pass

class StylingError(AlderError):
    """Erreur de style."""
    pass

class ThemingError(AlderError):
    """Erreur de thème."""
    pass

class BrandingError(AlderError):
    """Erreur de branding."""
    pass

class IdentityError(AlderError):
    """Erreur d'identité."""
    pass

class AuthenticationError(AlderError):
    """Erreur d'authentification."""
    pass

class AuthorizationError(AlderError):
    """Erreur d'autorisation."""
    pass

class PermissionError(AlderError):
    """Erreur de permission."""
    pass

class AccessError(AlderError):
    """Erreur d'accès."""
    pass

class SecurityError(AlderError):
    """Erreur de sécurité."""
    pass

class PrivacyError(AlderError):
    """Erreur de confidentialité."""
    pass

class ConfidentialityError(AlderError):
    """Erreur de confidentialité."""
    pass

class IntegrityError(AlderError):
    """Erreur d'intégrité."""
    pass

class AvailabilityError(AlderError):
    """Erreur de disponibilité."""
    pass

class ReliabilityError(AlderError):
    """Erreur de fiabilité."""
    pass

class DurabilityError(AlderError):
    """Erreur de durabilité."""
    pass

class MaintainabilityError(AlderError):
    """Erreur de maintenabilité."""
    pass

class ScalabilityError(AlderError):
    """Erreur de scalabilité."""
    pass

class PerformanceError(AlderError):
    """Erreur de performance."""
    pass

class EfficiencyError(AlderError):
    """Erreur d'efficacité."""
    pass

class OptimizationError(AlderError):
    """Erreur d'optimisation."""
    pass

class ResourceError(AlderError):
    """Erreur de ressource."""
    pass

class CapacityError(AlderError):
    """Erreur de capacité."""
    pass

class UtilizationError(AlderError):
    """Erreur d'utilisation."""
    pass

class AllocationError(AlderError):
    """Erreur d'allocation."""
    pass

class DeallocationError(AlderError):
    """Erreur de désallocation."""
    pass

class ManagementError(AlderError):
    """Erreur de gestion."""
    pass

class AdministrationError(AlderError):
    """Erreur d'administration."""
    pass

class OperationError(AlderError):
    """Erreur d'opération."""
    pass

class MaintenanceError(AlderError):
    """Erreur de maintenance."""
    pass

class SupportError(AlderError):
    """Erreur de support."""
    pass

class ServiceError(AlderError):
    """Erreur de service."""
    pass

class QualityError(AlderError):
    """Erreur de qualité."""
    pass

class ComplianceError(AlderError):
    """Erreur de conformité."""
    pass

class StandardError(AlderError):
    """Erreur de standard."""
    pass

class PolicyError(AlderError):
    """Erreur de politique."""
    pass

class RuleError(AlderError):
    """Erreur de règle."""
    pass

class RegulationError(AlderError):
    """Erreur de régulation."""
    pass

class GovernanceError(AlderError):
    """Erreur de gouvernance."""
    pass

class ControlError(AlderError):
    """Erreur de contrôle."""
    pass

class MonitoringError(AlderError):
    """Erreur de monitoring."""
    pass

class SupervisionError(AlderError):
    """Erreur de supervision."""
    pass

class OversightError(AlderError):
    """Erreur de supervision."""
    pass

class AuditError(AlderError):
    """Erreur d'audit."""
    pass

class InspectionError(AlderError):
    """Erreur d'inspection."""
    pass

class VerificationError(AlderError):
    """Erreur de vérification."""
    pass

class ValidationError(AlderError):
    """Erreur de validation."""
    pass

class CertificationError(AlderError):
    """Erreur de certification."""
    pass

class AccreditationError(AlderError):
    """Erreur d'accréditation."""
    pass

class LicensingError(AlderError):
    """Erreur de licence."""
    pass

class RegistrationError(AlderError):
    """Erreur d'enregistrement."""
    pass

class EnrollmentError(AlderError):
    """Erreur d'inscription."""
    pass

class SubscriptionError(AlderError):
    """Erreur d'abonnement."""
    pass

class MembershipError(AlderError):
    """Erreur d'adhésion."""
    pass

class AffiliationError(AlderError):
    """Erreur d'affiliation."""
    pass

class AssociationError(AlderError):
    """Erreur d'association."""
    pass

class PartnershipError(AlderError):
    """Erreur de partenariat."""
    pass

class CollaborationError(AlderError):
    """Erreur de collaboration."""
    pass

class CooperationError(AlderError):
    """Erreur de coopération."""
    pass

class CoordinationError(AlderError):
    """Erreur de coordination."""
    pass

class IntegrationError(AlderError):
    """Erreur d'intégration."""
    pass

class InteroperabilityError(AlderError):
    """Erreur d'interopérabilité."""
    pass

class CompatibilityError(AlderError):
    """Erreur de compatibilité."""
    pass

class PortabilityError(AlderError):
    """Erreur de portabilité."""
    pass

class AdaptabilityError(AlderError):
    """Erreur d'adaptabilité."""
    pass

class FlexibilityError(AlderError):
    """Erreur de flexibilité."""
    pass

class ExtensibilityError(AlderError):
    """Erreur d'extensibilité."""
    pass

class ModifiabilityError(AlderError):
    """Erreur de modifiabilité."""
    pass

class CustomizabilityError(AlderError):
    """Erreur de personnalisation."""
    pass

class ConfigurabilityError(AlderError):
    """Erreur de configuration."""
    pass 